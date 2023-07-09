import asyncio
import random
import requests
from datetime import datetime
import time
from typing import List, Dict, Union, Iterable, Callable, Tuple
# from exception import JockAPIException
# from objects import Team, Game, GameLog, Event, Tradeable, Entry, Order, Position, AccountActivity, Entity, \
#     _case_switch_ent
# from jm_sockets import sockets, sockets_update
from .exception import JockAPIException
from .objects import Team, Game, GameLog, Event, Tradeable, Entry, Order, Position, AccountActivity, Entity, \
    _case_switch_ent
from .jm_sockets import sockets, sockets_update
from decimal import Decimal, ROUND_DOWN


class Client(object):
    """The user should initialize an instance of this class:
    e.g. Client(secret, api_key)
    and then they should call whichever method they wish. The class will automatically obtain an auth token.
    Functionality included to auto update expired auth tokens or retreive new one if necessary.

    :ivar secret: The user's secret key: xxx
    :ivar api_key: the user's api key: jm_api_xxx

    """

    API_VERSION = 'v1'
    BASE_URL = 'https://api.jockmkt.net'
    WS_BASE_URL = 'wss://api.jockmkt.net/streaming/'
    _API_KEYS = {}
    _AUTH_TOKEN = {}
    _AUTH_TOKEN_MAP = {}
    _EXPIRATION = None
    _ATTEMPTS = 0
    LEAGUES = ['nba', 'nfl', 'nhl', 'pga', 'mlb', 'nascar']
    MLB_SCORING = {'at_bat': 0.5, 'single': 2.5, 'double': 3, 'triple': 3.5, 'home_run': 4, 'walk': 2, 'run': 2,
                   'rbi': 2, 'stolen_base': 3, 'strikeout': -1}
    NFL_SCORING = {'pass_yards': 0.04, 'pass_td': 4, 'int_thrown': -3, 'rush_yards': 0.1, 'rush_td': 6, 'reception': 1,
                   'receiving_yards': 0.1, 'receiving_td': 6, 'return_td': 6, 'two_pt_conversion': 2, 'fumble_lost': -3,
                   '100_yd_passing_bonus': 1, '100_yd_rushing_bonus': 3, '100_yd_receiving_bonus': 3}
    NBA_SCORING = {'point': 1, '10_pt_bonus': 1.5, '3pm': 0.5, 'rebound': 1.25, 'assist': 1.5, 'steal': 2, 'block': 2,
                   'turnover': -0.5, 'missed_fg': -0.5}
    NHL_SCORING = {'goal': 8.5, 'assist': 5, 'shot_on_goal': 1.5, 'blocked_shot': 2, 'shorthanded_pt': 2,
                   'shootout_goal': 1.5, 'hat_trick': 3, '3_plus_blocks': 3, '3_plus_pts': 3, 'penalty_mins': -0.5,
                   'hits': 1, 'goalie_win': 6, 'goalie_save': 0.5, 'goal_allowed': -3.5, 'ot_loss': 2,
                   '35_plus_saves': 3, 'shutout': 4}
    PGA_SCORING = {'win': 5, 'albatross': 4, 'eagle': 3, 'birdie': 2, 'par': 1, 'bogey': 0, 'double_bogey': -1,
                   'triple_bogey': -2, 'quadruple_bogey': -3, 'quintuple_bogey': -4}
    NASCAR_SCORING = {'lap_complete': 1, 'position': -1, 'win': 10, 'start_bonus': 40}
    ACCOUNT = {}
    balance = {}

    def __init__(self, secret, api_key, request_params=None, verbose=False):
        self._request_params = request_params
        self.secret = secret
        self.api_key = api_key
        user_auth = Client._AUTH_TOKEN_MAP.get(f'{api_key}:{secret}', None)
        self.auth = user_auth
        self.verbose = verbose
        self.balance = 0

    def _create_path(self, path, api_version=None):
        """generates a path for self._request
        """
        api_version = api_version or self.API_VERSION
        return '/{}/{}'.format(api_version, path)

    def _get_auth_token(self):
        payload = {
            'grant_type': 'client_credentials',
            'key': str(self.api_key),
            'secret': str(self.secret)
        }
        response = requests.post(f'{Client.BASE_URL}/{Client.API_VERSION}/oauth/tokens', data=payload).json()
        if self.verbose:
            print(response)
        if response['status'] == 'error':
            raise KeyError("Your authorization keys are not valid!")
        else:
            if self.verbose:
                print("Successfully obtained an auth token!")

        auth_token_dict = {'token': response['token']['access_token'], 'expired_at': response['token']['expired_at']}
        Client._AUTH_TOKEN_MAP[f'{self.api_key}:{self.secret}'] = auth_token_dict
        self.auth = auth_token_dict
        return auth_token_dict['token']

    @staticmethod
    def _build_auth_header(token):
        return {'Authorization': 'Bearer ' + token}

    def _request(self, method, path, api_version=None, attempt_number=0, **kwargs) -> Dict:
        """method by which all requests are made
        """
        response = {}
        auth = self.auth
        if auth is None:
            if self.verbose:
                print('no auth token')
            token = self._get_auth_token()
        elif auth['expired_at'] < round(time.time() * 1000):
            token = self._get_auth_token()
        else:
            token = auth['token']

        if self._request_params:
            kwargs.update(self._request_params)

        kwargs['data'] = kwargs.get('data', {})
        kwargs['params'] = kwargs.get('params', {})
        kwargs['payload'] = kwargs.get('payload', {})
        kwargs['is_test'] = kwargs.get('is_test', {})

        full_path = self._create_path(path, api_version)
        if method == 'get':
            kwargs['payload'] = kwargs.get('params')
            response = requests.get('{}{}'.format(self.BASE_URL, full_path), params=kwargs['payload'],
                                    headers=self._build_auth_header(token))

        if method == 'post':
            kwargs['payload'] = kwargs.get('data')
            response = requests.post('{}{}'.format(self.BASE_URL, full_path), data=kwargs['payload'],
                                     headers=self._build_auth_header(token))

        if method == 'delete':
            response = requests.delete('{}{}'.format(self.BASE_URL, full_path), headers=self._build_auth_header(token))

        res = self._handle_response(response, method, path, attempt_number=attempt_number, payload=kwargs)

        return res

    def _handle_response(self, json_response, method, path, attempt_number, **kwargs):
        """helper to handle api responses and determine exceptions
        """
        if json_response.status_code == 429 and 'tradeable_id' in kwargs['payload']['data']:
            order = kwargs.get('payload')
            is_test = order['is_test']
            return self._retry_order(order['data'], is_test=is_test)

        elif str(json_response.status_code).startswith('50'):
            payload = kwargs.get('payload')
            return self._retry_request(json_response, method, path, payload, attempt_number)

        elif not str(json_response.status_code).startswith('2'):
            raise JockAPIException(json_response)

        try:
            res = json_response.json()
            return res
        except ValueError:
            raise JockAPIException('Invalid Response: %s' % json_response.text)

    def _retry_request(self, json_response, method, path, payload, attempt_number):
        max_attempts = 3
        if attempt_number >= max_attempts:
            raise JockAPIException(json_response)
        backoff_times = [3, 10, 30]
        if self.verbose:
            print(
                f"Request failed. Code: {json_response.status_code}, Message: {json_response.json()['message']}. Retrying"
                f"in {backoff_times[attempt_number]} seconds")
        time.sleep(backoff_times[attempt_number])
        response = self._request(method, path, attempt_number=attempt_number + 1, payload=payload['payload'])

        if response['status'] == 'success':
            return response

    def _retry_order(self, order, **kwargs):
        next_minute = 60 - datetime.now().second
        if self.verbose:
            print(f"You've placed too many orders in the past minute. Sleeping for {next_minute} seconds")
        is_test = kwargs.get('is_test', False)
        if is_test:
            print('sleeping...')
            return 'successfully rerouted an order that would have failed.'
        else:
            time.sleep(next_minute)
        return self._post('orders', data=order)

    def _get(self, path, api_version=None, **kwargs):
        """method for get requests
        """
        return self._request('get', path, api_version, **kwargs)

    def _post(self, path, api_version=None, **kwargs):
        """method for post requests
        """
        return self._request('post', path, api_version, **kwargs)

    def _delete(self, path, api_version=None, **kwargs):
        """method for delete requests, used exclusively for order deletion
        """
        return self._request('delete', path, api_version, **kwargs)

    def get_account_bal(self) -> Dict:
        """method retreiving user's USD balance
        """
        Client.balance = self._get("balances")['balances']
        return self._get("balances")['balances']

    def get_account(self) -> Dict:
        Client.ACCOUNT = self._get('account')['account']
        return self._get('account')['account']

    def get_scoring(self, league: str) -> Dict[str, Dict[str, float]]:
        """
        method to retreive information about scoring for different league events

        :param league: the league for which you'd like to retreive scoring
        :type league:  str, required

        :returns:      scoring information for the chosen league
        :rtype:        dict
        """
        scoring_dict = {'mlb': self.MLB_SCORING,
                        'nhl': self.NHL_SCORING,
                        'nba': self.NBA_SCORING,
                        'pga': self.PGA_SCORING,
                        'nfl': self.NFL_SCORING,
                        'nascar': self.NASCAR_SCORING}

        return scoring_dict[league]

    def get_teams(self, start: int = 0, league: str = None) -> List[Team]:
        """provides a list of teams for all or chosen leagues that have team structure.
        displays only the first page, the user can paginate via:

        :param start: Which page the user wants to display. Default: 0 (first 100 teams)
        :type start: int, optional
        :param league: which league the user is searching for teams, one of: ['nba', 'nfl', 'nhl', 'pga', 'mlb', 'nascar']
        :type league: str, optional

        :returns: a list of Team objects
        :rtype: List[Team]
        """
        teams = []
        params = {'start': str(start * 100), 'limit': '100'}
        if league is not None:
            params['league'] = league
        res = self._get('teams', params=params)
        print('status: ' + res['status'])
        print('start: ' + str(res['start']))
        print('limit: ' + str(res['limit']))
        print('count: ' + str(res['count']))
        for team in res['teams']:
            teams.append(Team(team))
        return teams

    def get_team(self, team_id: str) -> Team:
        """fetch a specific team based on their team id

        :param team_id: a team id, starting with team (e.g. "team_8fe94ef0d1f0a00e1285301c4092650f")
        :type team_id: str, required

        :returns: a dictionary with team information
        :rtype: objects.Team
        """
        team = self._get(f"teams/{team_id}")['team']
        return Team(team)

    def get_entities(self, start: int = 0, limit: int = 100, include_team: bool = True, league: str = None,
                     include_count: bool = False) -> Union[List[Entity], Tuple[List[Entity], int]]:
        """fetch entities (players of any sport). The user will have to paginate.

        :param start: page at which the user wants to start their search, default: 0 (first page of entities)
        :type start: int, optional
        :param limit: number of entities the user wants to display, default: 100 (displays 100 entities)
        :type limit: int, optional
        :param include_team: include team information for the entity, default: False
        :type include_team: bool, optional
        :param league: filter by league, must be one of: ['nba', 'nfl', 'nhl', 'pga', 'mlb', 'nascar']
        :type league: str, optional
        :param include_count: include the count of available entities for this request as part of a tuple in the return value
        :type include_count: bool, optional

        :return: a list of league-specific Entity objects, or a tuple of the list and the available entity count.
        :rtype: List[objects.Entity] | Tuple[List[objects.Entity], int]
        """
        params = {}
        entities = []
        if league is not None:
            params['league'] = league
        if include_team:
            params['include'] = 'team'
        params['start'] = start * limit
        params['limit'] = limit
        res = self._get("entities", params=params)
        if self.verbose:
            print('status: ' + res['status'])
            print('start: ' + str(res['start']))
            print('limit: ' + str(res['limit']))
            print('count: ' + str(res['count']))
        for entity in res['entities']:
            entities.append(_case_switch_ent(entity))
        if include_count:
            return entities, res['count']
        return entities

    def get_entity(self, entity_id: str, include_team: bool = False) -> Entity:
        """fetch a specific entity based on their entity id

        :param entity_id: The chosen entity's id (e.g "en_9af7d442f918404feced51d877989aa0")
        :type entity_id: str, required
        :param include_team: include team information for the entity, default: False
        :type include_team: bool, optional

        :returns: a league-specific entity object, one of: :class:`objects.NBAEntity`, :class:`objects.NFLEntity`, :class:`objects.NHLEntity`, :class:`objects.NascarEntity`, :class:`objects.PGAEntity`, :class:`MLBEntity` which are all children of the :class:`objects.Entity`
        :rtype: objects.Entity

        """
        if include_team:
            params = {'include': 'team'}
        else:
            params = {}
        ent = self._get(f"entities/{entity_id}", params=params)['entity']
        return _case_switch_ent(ent)

    def get_games(self, start: int = 0, limit: int = 100, league: str = None, include_count: bool = False) -> \
            Union[List[Game], Tuple[List[Game], int]]:
        """provides a list of teams for all or chosen leagues that have team structure
        the user will have to paginate.

        :param start: page at which the user wants to start their search, default: 0 (first page of games)
        :type start: int, optioanl
        :param limit: number of entities the user wants to display, default: 100 (displays 100 recent and upcoming games)
        :type limit: int, optional
        :param league: filter by league, must be one of: ['nba', 'nfl', 'nhl', 'pga', 'mlb', 'nascar']
        :type league: str, optional
        :param include_count: include the count of available games for this request as part of a tuple in the return value
        :type include_count: bool, optional

        :returns: A list of :class:`objects.Game` objects
        :rtype: list

        """
        params = {}
        games = []
        params['start'] = start * limit
        params['limit'] = limit
        if league is not None:
            params['league'] = league
        res = self._get('games', params=params)
        if self.verbose:
            print('status: ' + res['status'])
            print('start: ' + str(res['start']))
            print('limit: ' + str(res['limit']))
            print('count: ' + str(res['count']))
        for game in res['games']:
            games.append(Game(game))
        if include_count:
            return games, res['count']
        return games

    def get_game(self, game_id: str) -> Game:
        """fetch a specific entity based on their entity id

        :param game_id: a string of the game id (e.g. "game_60bb686586eaf95a5e8dafa3823d89cb")
        :type game_id: str, required

        :returns: a :class:`objects.Game` object, containing the relevant fields
        :rtype: objects.Game

        """
        return Game(self._get(f"games/{game_id}")['game'])

    def get_game_logs(self, start: int = 0, limit: int = 100, log_id: str = None, entity_id: str = None,
                      game_id: str = None, include_ent: bool = True, include_game: bool = False,
                      include_team: bool = False, include_count: bool = False) -> Union[
        List[GameLog], Tuple[List[GameLog], int]]:
        """fetch game logs

        :param start: Page at which the user wants to start their search, default: 0
            (first page of game_logs)
        :type start: int, optional
        :param limit: Number of entities the user wants to display, default: 100 (displays 100 game_logs)
        :type limit: int, optional
        :param log_id: Filter for a specific log or list of logs
            (e.g. "gl_60cde7f973f9e00674785e5e144a802b")
        :type log_id: str or list of str, optional
        :param entity_id: Filter all game logs for a specific player,
            (e.g. "en_67c8368a3905f8beee69393ccec854e5")
        :type entity_id: str, optional
        :param game_id: filter all game logs for all players in a specific game,
            (e.g. "game_60cde69ee06e791b99ed71e6013fc4a7")
        :type game_id: str, optional
        :param include_ent: Returns entity information attached to the game log (entity name, team, etc.)
        :type include_ent: bool, optional
        :param include_game: Returns game information (game name, teams, status)
        :type include_game: bool, optional
        :param include_team: Returns team information (team name, location, league, etc.)
        :type include_team: bool, optional
        :param include_count: include the count of available game logs for this request as part of a tuple in the return value
        :type include_count: bool, optional

        :returns: a list of :class:`objects.GameLogs`, containing scoring information for a player in a specific game.
        If include_count == True, it will be at tuple of the list of logs and an integer for count of game logs available.
        :rtype: objects.GameLog | Tuple[objects.GameLog, int]

        """
        params = {}
        include = []
        game_logs = []
        if log_id is not None:
            params['id'] = log_id
        if entity_id is not None:
            params['entity_id'] = entity_id
        if game_id is not None:
            params['game_id'] = game_id
        if include_game:
            include.append('game')  # can be computationally costly for golf events, be careful
        if include_ent:
            include.append('entity')
        if include_team:
            include.append('team')
        if len(include) != 0:
            params['include'] = str(include)
        params['start'] = start * limit
        params['limit'] = limit
        res = self._get("game_logs", params=params)
        if self.verbose:
            print('status: ' + res['status'])
            print('start: ' + str(res['start']))
            print('limit: ' + str(res['limit']))
            print('count: ' + str(res['count']))
        for log in res['game_logs']:
            game_logs.append(GameLog(log))
        if include_count:
            return game_logs, res['count']
        return game_logs

    def get_events(self, start: int = 0, limit: int = 25, league: str = None, include_sims: bool = False,
                   include_count: bool = False) \
            -> Union[
                List[Event], Tuple[List[Event], int]]:
        """Populates event objects with recent and upcoming events

        :param start: Page at which the user wants to start their search, default: 0 (first page of events)
        :type start: int, optional
        :param limit: Number of entities the user wants to display,
            default: 25 (displays 25 recent and upcoming events)
        :type limit: int, optional
        :param league: Filter by league, must be one of: ['nba', 'nfl', 'nhl', 'pga', 'mlb', 'nascar']
        :type league: str, optional
        :param include_sims: Will return all events, including Horse Sims for test use
        :type include_sims: bool, optional
        :param include_count: include the count of available events for this request as part of a tuple in the return value
        :type include_count: bool, optional

        :returns: list of :class:`objects.Events`, containing the event_id and information for each
        :rtype: List[objects.Event]

        """
        print('fetching events')
        list_events = []
        data = {'start': str(start * limit), 'limit': limit}
        if league is not None:
            data['league'] = league
        res = self._get('events', params=data)
        if self.verbose:
            print('status: ' + res['status'])
            print('start: ' + str(res['start']))
            print('limit: ' + str(res['limit']))
            print('count: ' + str(res['count']))
        for event in res['events']:
            if event['league'] != 'simulated_horse_racing':
                list_events.append(Event(event))
            elif include_sims:
                list_events.append(Event(event))
        if include_count:
            return list_events, res['count']
        return list_events

    def get_event(self, event_id: str) -> Event:
        """fetch a particular event, by default includes games, payouts and tradeables. This is easier than
        pulling payouts, tradeables, and games separately

        :param event_id: The event_id for your chosen event, (e.g. evt_60dbec530d2197a973c5dddcf6f65e12)
        :type event_id: str, required

        :returns: An :class:`objects.Event`, including its payouts, tradeables and games
        :rtype: objects.Event

        """
        params = {}
        include = ['tradeables.entity', 'games', 'payouts']
        params['include'] = str(include)
        res = self._get(f"events/{event_id}", params=params)
        return Event(res['event'])

    def get_event_payouts(self, event_id: str) -> dict:  # should this be appended to the event object itself?
        """get payouts for each rank of an event

        :param event_id: The event_id for your chosen event, (e.g. evt_60dbec530d2197a973c5dddcf6f65e12)
        :type event_id: str, required

        :returns: a dictionary of the chosen event's payouts
        :rtype: dict

        """
        return self._get(f"events/{event_id}/payouts")

    def get_event_games(self, event_id: str) -> List[Game]:
        """get all games in an event

        :param event_id: the event_id for your chosen event, (e.g. evt_60dbec530d2197a973c5dddcf6f65e12)
        :type event_id: str, required

        :returns: a list of event-relevant :class:`objects.Game` objects
        :rtype: List[objects.Game]

        """
        games = []
        res = self._get(f"events/{event_id}/games")
        for game in res['games']:
            games.append(Game(game))
        return games

    def get_event_tradeables(self, event_id: str) -> List[Tradeable]:
        """get all tradeables in an event

        :param event_id: The event_id for your chosen event, (e.g. evt_60dbec530d2197a973c5dddcf6f65e12)
        :type event_id: str, required

        :returns: a list of :class:`objects.Tradeable` objects participating in the chosen event
        :rtype: List[objects.Tradeable]

        """
        res = self._get(f"events/{event_id}/tradeables")
        tradeables = []
        for tdbl in res['tradeables']:
            tradeables.append(Tradeable(tdbl))
        return tradeables

    def get_entries(self, start: int = 0, limit: int = 10, include_payouts: bool = False,
                    include_tradeables: bool = False, include_count: bool = False) -> Union[
        List[Entry], Tuple[List[Entry], int]]:
        """obtain information about events a user has entered

        :param start: Page at which the user wants to start their search,
            default: 0 (first page of entries)
        :type start: int, optional
        :param limit: Number of entities the user wants to display, default: 10 (displays 10 recent
            and upcoming entries)
        :type limit: int, optional
        :param include_payouts: Option to include payouts of completed entries, default: False
        :type include_payouts: bool, optional
        :param include_tradeables: Option to include entry-relevant :class:`objects.Tradeable` objects
        :type include_tradeables: bool, optional
        :param include_count: Include the total entry count as part of a returned tuple
        :type include_count: bool, optional

        :returns: A list of :class:`objects.Entry` objects, or a tuple of the list and an int representing the total number of entries.
        :rtype: object.Entry | tuple(list[object.Entry], int)

        """
        params = {'start': start * limit, 'limit': limit}
        include = ['event']
        if include_payouts:
            include.append('payouts')
        if include_tradeables:
            include.append('payouts.tradeable')
        params['include'] = str(include)
        response_list = []
        res = self._get("entries", params=params)
        if self.verbose:
            print('status: ' + res['status'])
            print('start: ' + str(res['start']))
            print('limit: ' + str(res['limit']))
            print('count: ' + str(res['count']))
        for entry in res['entries']:
            response_list.append(Entry(entry))
        if include_count:
            return response_list, res['count']
        return response_list

    def get_entry(self, entry_id: str, include_event: bool = False, include_payouts: bool = False,
                  include_tradeables: bool = False) -> Entry:
        """Method to obtain information about an event that a user has entered. include_payouts and include_tradeables
        will only provide info after the event is paid out.

        :param entry_id: The entry_id for which the user wishes to get information
            (e.g. evt_60dbec530d2197a973c5dddcf6f65e12)
        :type entry_id: str, required
        :param include_event: Include :class:`objects.Event` information related to the entry
        :type include_event: bool, optional
        :param include_payouts: Include payouts for the user's holdings of a completed event
        :type include_payouts: bool, optional
        :param include_tradeables: Include relevant event :class:`object.Tradeable` objects
        :type include_tradeables: bool, optional

        :returns: a list of :class:`objects.Entry` objects, containing the user's chosen fields
        :rtype: objects.Entry

        """
        params = {}
        include = []
        if include_event:
            include.append('event')
        if include_payouts:
            include.append('payouts')
        if include_tradeables:
            include.append('payouts.tradeable')
        if len(include) != 0:
            params['include'] = str(include)
        entry = self._get(f"entries/{entry_id}", params=params)
        return Entry(entry['entry'])

    def create_entry(self, event_id: str) -> Dict:
        """create an entry to an event given an event_id e.g. evt_60dbec530d2197a973c5dddcf6f65e12

        :param event_id: the event_id for which the user would like to create an entry to
        :type event_id: str, required
        """
        try:
            return self._post(f"entries", data={'event_id': event_id})
        except JockAPIException:
            print('Event already joined.')

    def place_order(self, id: str, price: float, qty: int = 1, side: str = 'buy', phase: str = 'ipo', **kwargs) \
            -> Union[Order, Dict]:
        """
        Places an order of the user's chosen tradeable (player) and the chosen price. It defaults to  buy 1 share
        during the ipo phase. The user may specify an amount of money they want to buy and automatically buy x shares at
        the chosen price (param: order_size), such that the total cost is less than their specified amount. If the user
        wants to make a live they must specify phase='live', or if they want to sell a share side='sell'.

        :param id: The chosen player's tradeable id, obtained by calling a Tradeable object
        :type id: str, required
        :param price: The user's chosen price at which to place their order
        :type price: int, required
        :param side: default: 'buy' - the user must specify 'sell' if they wish to sell
        :type side: str, optional
        :param phase: default: 'ipo' - If the Event.status is 'ipo', should be ipo, else specify 'live'
        :type phase: str, optional
        :param qty: default: 1 - The desired number of shares the user wants to buy, the user may specify order_size instead.
        :type qty: int, optional
        :param order_size: The user can specify the total amount they wish to spend on shares of a player. Calculated by: (order_size)//price (it will always round down)
        :type order_size: int, optional

        :returns: A json response with information about the order that was sent

        """
        if price > 25:
            price = 25

        if 'order_size' in kwargs:
            size = kwargs.get('order_size', 0)
            qty = size // price

        price = Decimal(price).quantize(Decimal('0.00'), rounding=ROUND_DOWN)

        price = "{:.2f}".format(price)

        order = {'tradeable_id': id, 'side': side, 'type': 'limit', 'phase': phase, 'quantity': str(qty),
                 'limit_price': price}
        order_response = self._post('orders', data=order, is_test=kwargs.get('is_test', False))

        if type(order_response) == str:
            return order_response

        return Order(order_response['order'])

    # NOTE: the docs for order object > status contain 'outbid' twice

    def get_orders(self, start: int = 0, limit: int = 100, event_id: str = None, active: bool = False,
                   updated_after: int = None, include_count=False) -> Union[List[Order], Tuple[List[Order], int]]:
        """Get all of a user's orders. The user is required to paginate if they want to see more than 1 page

        :param start: Page at which the user wants to start their search, default: 0 (first page of entities)
        :type start: int, optional
        :param limit: Number of entities the user wants to display, default: 100 (displays 100 entities)
        :type limit: int, optional
        :param event_id: the event_id for your chosen event, (e.g. evt_60dbec530d2197a973c5dddcf6f65e12)
        :type event_id: str, optional
        :param active: Whether to display only orders that are active (either created or accepted),
            default = False
        :type active: bool, optional
        :param updated_after: filter orders updated after 13 digit epoch timestamp (orders with fills,
            partial fills, cancellations, outbids, etc. after that time)
        :type updated_after: int, optional
        :param include_count: Include the number of TOTAL orders in the return value.
        :type include_count: bool, option

        :returns: a list of :class:`objects.Order` objects | a tuple of a list of :class:`objects.Order` and an int representing total order count.
        :rtype: objects.Order

        """
        params = {'start': start * limit, 'limit': limit}
        orders = []
        if event_id is not None:
            params['event_id'] = str(event_id)
        if active:
            params['active'] = 'true'
        if updated_after is not None:
            params['updated_after'] = str(updated_after)
        orders_response = self._get('orders', params=params)
        if self.verbose:
            print('status: ' + orders_response['status'])
            print('start: ' + str(orders_response['start']))
            print('limit: ' + str(orders_response['limit']))
            print('count: ' + str(orders_response['count']))
        for order in orders_response['orders']:
            orders.append(Order(order))
        if include_count:
            return orders, orders_response['count']
        return orders

    def get_order(self, order_id: str) -> Order:
        """get information about a specific order

        :param order_id: Order id for which the user is searching `(e.g. ord_601b5ad6538ec34875ee1687c4a657f8)`
        :type order_id: str, required

        :returns: :class:`objects.Order`
        :rtype: Order

        """
        return Order(self._get(f"orders/{order_id}")['order'])

    def delete_order(self, order_id: str) -> Dict:
        """delete a specific order

        :param order_id: order id for which the user is attempting to delete
            (e.g. ord_601b5ad6538ec34875ee1687c4a657f8)
        :type order_id: str, required

        :returns: json response with information about the order deletion

        """
        deletion_res = self._delete(f"orders/{order_id}")
        if deletion_res['status'] == 'success':
            if self.verbose:
                print('order successfully canceled')
        print(deletion_res)
        return deletion_res

    def get_positions(self, include_count: bool = False) -> Union[List[Position], Tuple[List[Position], int]]:
        """
        :param include_count: Include the total positions count as the second part of a tuple in return value
        :type include_count: bool, optional

        :returns: a user's open positions in all current events, and if include_count==True, the total count of positions.
        """
        positions = []
        positions_res = self._get("positions")
        if self.verbose:
            print('status: ' + positions_res['status'])
            print('count: ' + str(positions_res['count']))
        for position in positions_res['positions']:
            positions.append(Position(position))
        if include_count:
            return positions, positions_res['count']
        return positions

    def get_account_activity(self, start: int = 0, limit: int = 100) -> List[AccountActivity]:
        """
        returns a user's most recent account activity

        :param start: the page of account activity which the user wants to display,
            default = 0 (first page of responses)
        :type start: int, optional
        :param limit: the quantitiy of account activity objects the user wants to see, default = 100
        :type limit: int, optional

        :returns: a list of :class:`objects.AccountActivity`
        :rtype: List[AccountActivity]

        """
        params = {'start': str(start * limit), 'limit': limit}
        activity_res = self._get('account/activity', params=params)
        acct_activity = []
        for aact in activity_res['activity']:
            acct_activity.append(AccountActivity(aact))
        return acct_activity

    def ws_token_generator(self):
        self._get('account')
        return self.auth['token']

    def get_ws_topics(self) -> Dict[str, Dict]:
        """
        returns a dictionary of websocket topics and their required arguments
        """
        topics = {'event': {'required_args': 'event_id'},
                  'event_activity': {'required_args': 'event_id'},
                  'account': {'required_args': None},
                  'notifications': {'required_args': None},
                  'games': {'required_args': 'league', 'options':
                      self.LEAGUES}}

        return topics

    def ws_connect(self, loop: Union[asyncio.AbstractEventLoop, asyncio.BaseEventLoop], queue: List,
                   error_handler: Callable, callback=None):
        """
        Initialize a websocket connection. See docs for example code.

        :param loop:          An asyncio loop, i.e. asyncio.get_event_loop
        :type loop:           asyncio.Event, required
        :param queue:         A list that websocket messages will be pushed to
        :type queue:          iterable, required
        :param error_handler: a method for handling errors. The user can pass socket.reconnect here
        :type error_handler:  Callable, required
        """

        return sockets.JockmktSocketManager.create(loop, self, queue, error_handler, callback, ws_url=self.WS_BASE_URL)

    def ws_connect_new(self, loop: Union[asyncio.AbstractEventLoop, asyncio.BaseEventLoop], queue: List,
                       error_handler: Callable, subscriptions: List[Dict],
                       callback: Callable = None):
        """
        Initialize a websocket connection. See docs for example code.

        :param loop:          An asyncio loop, i.e. asyncio.get_event_loop
        :type loop:           asyncio.Event, required
        :param queue:         A list that websocket messages will be pushed to
        :type queue:          iterable, required
        :param error_handler: a method for handling errors. The user can pass socket.reconnect here
        :type error_handler:  Callable, required
        :param subscriptions: A list of subscriptions, each is a dictionary: {'endpoint': endpoint,
                                                                              'event_id': event_id,                                                                   'league': league}
        """
        return sockets_update.JockmktSocketManager.create(loop, self, queue, error_handler, subscriptions, callback,
                                                          ws_url=self.WS_BASE_URL)
