import asyncio
import json
import logging
import typing
import sys
# sys.path.insert(1, '..')
# from objects import Game, Event, Tradeable, Entry, Order, Position, PublicOrder, Trade, Balance
# from exception import JockAPIException
from ..objects import Game, Event, Tradeable, Entry, Order, Position, PublicOrder, Trade, Balance
from ..exception import JockAPIException
import ssl
import certifi
import websockets as ws


class JockmktSocketManager:
    MAX_RECONNECTS = 5
    AUTH_DICT = {}
    PUBLIC_TOPICS = {
        "event_activity": "event_id",
        "event": "event_id",
        "account": None,
        "notification": None,
        "games": "league"
        }

    def __init__(self, iterable, url: str='wss://api.jockmkt.net/streaming/'):
        self._subscriptions = []
        self.messages = iterable
        self.balances = {}
        self.close = False
        self._coro = None
        self._socket = None
        self.conn = None
        self._loop = None
        self._client = None
        self._subscribed = []
        self._reconnect_attempts = 0
        self.log = logging.getLogger(__name__)
        self.url = url
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.load_verify_locations(certifi.where())
        self._error_handler = None

    @classmethod
    async def create(cls, loop, client, iterable, error_handler, subscriptions,  coro, ws_url):
        self = JockmktSocketManager(iterable, ws_url)
        self._client = client
        self._loop = loop
        self._error_handler = error_handler
        self._coro = coro
        self._subscriptions = subscriptions
        self.__build_auth_dict(client.ws_token_generator())
        self.conn = asyncio.ensure_future(self._run(), loop=self._loop)
        return self

    def __build_auth_dict(self, token):
        """
        builds the dictionary necessary for the websocket authorization
        """
        auth_dict = {"action": "authenticate", "authentication": {"type": "token", "token": token}}
        self.AUTH_DICT = auth_dict
        return auth_dict

    async def _run(self):
        """
        authorizes websocket and receives messages

        PUT SUBSCIPTIONS IN THE CONNECT METHOD
        """
        async with ws.connect(self.url, ssl=self.ssl_context) as socket:
            self._socket = socket
            self._reconnect_attempts = 0
            try:
                await self.send_message(self.AUTH_DICT)
                auth_response = await self._socket.recv()
                auth_response = json.loads(auth_response)
                if auth_response['status'] != 'success':
                    raise JockAPIException('Unable to authorize the websocket connection')
                else:
                    if self._client.verbose:
                        print('Successfully connected to websockets.')

                for sub in self._subscriptions:
                    endpoint = sub.get('endpoint')
                    event_id = sub.get('event_id')
                    league = sub.get('league')
                    await self.subscribe(endpoint, event_id, league)
                    if self._client.verbose:
                        print('subscribed to {} {} {}'.format(endpoint,
                                                          f'event_id={event_id}' if event_id is not None else "",
                                                          f'league={league}' if league is not None else ""))

                async for message in socket:
                    await self._recv(message)
            except ws.ConnectionClosed as on_close:
                self.log.debug(f'Connection closed: {on_close}')
                await self.cancel()

            except ws.ConnectionClosedError as on_close:
                self.log.debug(f'Connection terminated with an error: {on_close}')
                await self._error_handler(message, on_close)

            except asyncio.CancelledError:
                pass

            except Exception as e:
                self.log.debug(f'Unkown ws exception: {e}')
                await self._error_handler(message, e)

            await self.cancel()

    async def reconnect(self):
        """
        An error handler is required, so this is a good option! it just attempts to reconnect upon failure
        """
        await self.cancel()
        self._reconnect_attempts += 1
        if self._reconnect_attempts < self.MAX_RECONNECTS:
            wait = self._get_reconnect_wait(self._reconnect_attempts)
            self.log.debug(f'websockets reconnecting. Attempting {self._reconnect_attempts} more times after waiting '
                           f'{wait} seconds')
            self.conn = asyncio.ensure_future(self._run(), loop=self._loop)
        else:
            self.log.error('websocket could not reconnect after 5 attempts.')
            self._socket.close()

    @staticmethod
    def _get_reconnect_wait(attempts):
        wait = [0.1, 3, 10, 30, 60]
        return wait[attempts]

    async def send_message(self, msg, retry_count=0):
        """
        send a message to the websocket (i.e. subscribe or unsubscribe). The user typically should not need to use this.
        """
        if not self._socket:
            if retry_count < 5:
                await asyncio.sleep(1)
                await self.send_message(msg, retry_count + 1)
        else:
            await self._socket.send(json.dumps(msg))

    async def cancel(self):
        """
        cancels the instance of websocket connection
        """
        try:
            self.conn.cancel()
            cancelled = self.conn.cancelled()
            while not cancelled:
                cancelled = self.conn.cancelled()
                if self._client.verbose:
                    print('Waiting for websocket connection cancellation')
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    def _wsfeed_case_switcher(self, obj, msg):
        orig = obj
        if obj == 'error':
            raise Exception(f'{msg}')
        elif obj == 'balances':
            self.balances[msg[obj]['currency']] = msg[obj]['buying_power']
        elif obj == 'order':
            if 'limit_price' in msg[obj]:
                obj = 'user_order'
            else:
                obj = 'public_order'
        elif obj == 'subscription':
            return msg
        ws_case_dict = {
            'tradeable': Tradeable,
            'game': Game,
            'event': Event,
            'entry': Entry,
            'position': Position,
            'user_order': Order,
            'public_order': PublicOrder,
            'trade': Trade,
            'balance': Balance,
            'notification': dict
        }
        if type(msg) == str:
            msg = json.loads(msg)

        return ws_case_dict[obj](msg[orig])

    async def _recv(self, msg):
        """
        handle incoming messages. The user should pass their event handling function in as an arg to callback
        """
        if self.messages is not None:
            messsage = json.loads(msg)
            type = messsage['object']
            obj = self._wsfeed_case_switcher(type, messsage)
            messsage[type] = obj
            self.messages.append(messsage)

        if self._coro is not None:
            await self._coro(msg)

    async def subscribe(self, topic: str, id: str = None, league: str = None):
        """
        Subscribe to a chosen topic or event.

        :param topic:  The user's chosen topic. Use client.get_ws_topics() for available topics.
        :type topic:   str, required
        :param id:     The event ID, required if you are subscribing to event or event_activity.
        :type id:      str, optional
        :param league: the league for which the user wants game data, required for 'games' subscription
        :type league:  str, optional
        """
        topics = self.PUBLIC_TOPICS.keys()
        if topic not in topics:
            raise KeyError(f'please choose from the following topics: {list(topics)}')
        self._subscribed.append((topic, id, league))
        msg = {"action": "subscribe",
               "subscription": {"type": str(topic),
                                'event_id': id,
                                'league': league}}
        await self.send_message(msg)

    async def unsubscribe(self, topic: str, id: str = None, league: str = None):
        """
        unsubscribe method

        :param topic:  The user's chosen topic. Use client.get_ws_topics() for available topics.
        :type topic:   str, required
        :param id:     The event ID, required if you are subscribing to event or event_activity.
        :type id:      str, optional
        :param league: the league for which the user wants game data, required for 'games' subscription
        :type league:  str, optional
        """
        msg = {"action": "unsubscribe",
               "subscription": {"topic": topic,
                                "event_id": str(id),
                                "league": str(league)}}
        await self.send_message(msg)

    async def unsubscribe_all(self):
        """
        unsubscribe all method
        """
        for i in self._subscriptions:
            await self.unsubscribe(topic=i[0], id=i[1], league=i[2])