==========
Websockets
==========

.. websockets_

Websockets allow the user to connect to a range of endpoints and receive continuous updates without having to ping the api again. Most websocket messages containing Tradeables, Games, Events, Entries, Positions, Orders and Trades will be converted to objects instead of just dictionaries. Their attributes can be accessed via a '.'

**the available sockets are as follows:**

- event
    - updates information about an event and the tradeables within the event

- event_activity
    - information regarding orders being placed by other users, trades that are made

- games
    - information about games that are currently live for a given league
    - Available leagues: ['mlb', 'nhl', 'nfl', 'nba', 'pga', 'nascar']

- account
    - Updates on balances, orders, positions, orders

- notification
    - notifications about order fills, events closing, and outbids

.. py:currentmodule:: jockmkt_sdk.client

.. automethod:: Client.get_ws_topics

**Browse websocket topics:**

.. code-block::

    client.get_ws_topics()

.. automethod:: Client.ws_connect

**Connect to a websocket:**

    client.ws_connect(loop, queue, error_handler)

- Client.ws_connect()

- args:
    - *loop:* an asyncio loop. see example below.
    - *queue:* an iterable (usually a list) in which you want your messages to be stored.
    - *error_handler:* an async function that handles errors. Defaults to .reconnect.

.. code-block::

    socket_manager = await client.ws_connect(loop, queue=msg_list, error_handler=error_handler)

.. important::

    you must **await** client.ws_connect()! You cannot simply call it, since it is an asynchronous function.


**Alternative websocket connection method:**

    client.ws_connect_new(loop, queue, error_handler, subscriptions)

- args:
    - *loop:* an asyncio loop. see example below.
    - *queue:* an iterable (usually a list) in which you want your messages to be stored.
    - *error_handler:* an async function that handles errors. Defaults to .reconnect.
    - *subscriptions:* a list of subscriptions in the following format:
- This function will handle all subscriptions in one go, rather than requiring the user to call .subscribe()

.. code-block:: python

    subscriptions = [
        {'endpoint': 'account'},

        {'endpoint': 'event',
        'event_id': 'evt_xxx'},

        {'endpoint': 'games',
        'league': 'nfl'}
    ]

    sm = await client.ws_connect_new(loop, queue: List, error_handler: Callable, subscriptions: List[Dict]=subscriptions)

.. note::

    You should await Client.ws_connect_new().

.. currentmodule:: jockmkt_sdk.jm_sockets.sockets

.. autoclass:: JockmktSocketManager

**JockmktSocketManager**

- *available instance variables:*
    - *messages:* the iterable to which the user wants to append messages
    - *balances:* regularly updated balances, including cash and contest balances.

- **available methods within the JockmktSocketManager class**

.. automethod:: JockmktSocketManager.subscribe

- *JockmktSocketManager.subscribe()*
    - Subscribe to a single topic
    - *params:*
        - *topic:* str, required, the user's chosen topic. use client.get_ws_topics() for info.
        - *id:* str, required if you are subscribing to 'event' or 'event_activity'
        - *league:* str, required if you are subscribing to 'games'

.. automethod:: JockmktSocketManager.unsubscribe

- *JockmktSocketManager.unsubscribe()*
    - unsubscribe from a single topic
    - *params:*
        - *topic:* str, required, the user's chosen topic. use client.get_ws_topics() for info.
        - *id:* str, required if you are subscribing to 'event' or 'event_activity'
        - *league:* str, required if you are subscribing to 'games'

.. automethod:: JockmktSocketManager.unsubscribe_all

- *JockmktSocketManager.unsubscribe_all()*
    - unsubscribe from a single topic

.. automethod:: JockmktSocketManager.reconnect


.. websocket examples_

Example
=======

.. code-block:: python

    import asyncio
    import time
    from datetime import datetime
    import pandas as pd
    from jockmkt_sdk.client import Client

    client = Client('<secret_key>', '<api_key>')

    async def main():
        global loop #  our asyncio loop defined below
        global client #  our client instance
        queue = [] #  list to which we will append all of our websocket responses as dictionaries

        async def error_handler(**kwargs):
            """
            defining an error handler, which is required. You may use `JockmktSocketManager.reconnect` here for
            a simple reconnect method. It will attempt 5 reconnects before raising an error.
            """
            await socket_manager.reconnect()

        game_info = []
        event_info = []
        #  push different message types to different lists
        async def handle_queue(msg):
            print(msg)
            if msg['subscription'] == 'games':
                game_info.append(msg)
            if msg['subscription'] == 'event':
                event_info.append(msg)

        socket_manager = await client.ws_connect(loop=loop, queue=queue, error_handler=error_handler)

        event_details = client.get_event(event_id)

        await socket_manager.subscribe('games', league='mlb') #  subscribe to all MLB game info
        await socket_manager.subscribe('account') #  subscribe to all account info
        await socket_manager.subscribe('event', id=event_id) #  subscribe to all event-specific information
        await socket_manager.subscribe('event_activity', id=event_id) #  subscribe to all event-specific order & trade information
        await socket_manager.subscribe('notifications') #  subscribe to all user notifications

        # Run the loop until 20 minutes after the event is projected to end
        while time.time() - 1200 < event_details.est_close:
            await asyncio.sleep(5)
            async for message in socket_manager.messages:
                await handle_queue(i)
                queue.remove(i)

        game_info_to_df = [] #  push all game info results to a list for conversion to df
        for game_update in game_info:
            game_info_to_df.append(game_update['game'].__dict__)

        #  save a dataframe of all game updates for future analysis!
        date = datetime.fromtimestamp(event_details.ipo_end)
        game_info_df = pd.DataFrame(game_info_to_df)
        game_info_df.to_csv(f'{event_details.name}_gamedata_{date}.csv')

    if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())

