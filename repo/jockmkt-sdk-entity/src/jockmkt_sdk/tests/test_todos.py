import unittest.mock
from unittest import mock, main, TestCase
import pytest
import sys
import json
from datetime import datetime

from jockmkt_sdk import client, objects


authorization_res = json.load(open('./test_resources/authorization.json'))
account_activity_res = json.load(open('./test_resources/account_activity.json'))
entities_res = json.load(open('./test_resources/entities.json'))
entry_res = json.load(open('./test_resources/entry.json'))
event_res = json.load(open('./test_resources/event.json'))
events_res = json.load(open('./test_resources/events.json'))
game_logs_res = json.load(open('./test_resources/game_logs.json'))
games_res = json.load(open('./test_resources/games.json'))
orders_res = json.load(open('./test_resources/orders.json'))
position_res = json.load(open('./test_resources/position.json'))
place_order_res = json.load(open('./test_resources/order_place.json'))
order_limit_res = json.load(open('./test_resources/order_rate_limit.json'))

_test_api_key = "jm_key_xxx"
_test_secret_key = "xxx"
_test_auth_token = 'eyXXX'
_test_auth_expiration1 = round(datetime.now().timestamp() * 1000)
_test_auth_expiration2 = round(((datetime.now().timestamp()) + 2592000) * 1000)
_test_auth_expired = round((datetime.now().timestamp() - 3600) * 1000)
_test_auth_dict = {'token': _test_auth_token, 'expired_at': _test_auth_expiration2}

mock_auth_header = {'Authorization': f'Bearer {_test_auth_token}'}

class TestClient(TestCase):
    mock_init = client.Client(_test_secret_key, _test_api_key)

    def test_build_auth_token(self):
        _test_bearer_object = f'Bearer {_test_auth_token}'
        test_header = self.mock_init._build_auth_header(_test_auth_token)
        self.assertEqual(test_header['Authorization'], _test_bearer_object)

    @mock.patch("jockmkt_sdk.client.requests.post")
    def test_get_auth_token(self, get_auth_token_mock):
        mock_auth_response = mock.Mock(status_code=200)
        mock_auth_response.json.return_value = authorization_res
        get_auth_token_mock.return_value = mock_auth_response

        mock_key_map = f'{_test_api_key}:{_test_secret_key}'
        mock_auth_request = self.mock_init._get_auth_token()

        mock_auth_dict = {'token': mock_auth_response.json()['token']['access_token'],
                          'expired_at': mock_auth_response.json()['token']['expired_at']}
        self.assertEqual(mock_auth_request, _test_auth_token)
        self.assertIn(mock_key_map, self.mock_init._AUTH_TOKEN_MAP)
        self.assertEqual(self.mock_init._AUTH_TOKEN_MAP[mock_key_map], mock_auth_dict)

    @mock.patch("jockmkt_sdk.client.requests.post")
    def test_place_order(self, place_order_mock):
        mock_place_order_response = mock.Mock(status_code=200)
        mock_place_order_response.json.return_value = place_order_res
        self.mock_init.auth = _test_auth_dict
        place_order_mock.return_value = mock_place_order_response
        mock_order_place = self.mock_init.place_order('tdbl_xxx', price=10, side='buy', phase='ipo', quantity=10)
        self.assertEqual(mock_order_place, mock_order_place)

    @mock.patch('jockmkt_sdk.client.requests.post')
    def test_handle_429_response(self, handle_response_mock):
        mock_order_error_res = mock.Mock(status_code=429)
        mock_order_error_res.json.return_value = order_limit_res
        handle_response_mock.return_value = mock_order_error_res
        self.mock_init.auth = _test_auth_dict
        mock_order_place = self.mock_init.place_order('tdbl_xxx', price=10, side='buy', phase='ipo', quantity=10,
                                                      is_test=True)
        self.assertEqual(mock_order_place, 'successfully rerouted an order that would have failed.')

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_events(self, get_events_mock):
        mock_events_response = mock.Mock(status_code=200)
        mock_events_response.json.return_value = events_res
        self.mock_init.auth = _test_auth_dict
        get_events_mock.return_value = mock_events_response

        mock_events_request = self.mock_init.get_events()
        print(mock_events_request[2])
        print(objects.Event(events_res['events'][2]))
        self.assertEqual(mock_events_request[2].name, objects.Event(events_res['events'][2]).name)
        self.assertIsInstance(mock_events_request[0], objects.Event)

    @mock.patch("jockmkt_sdk.client.requests.get")
    def test_get_event(self, get_event_mock):
        mock_event_response = mock.Mock(status_code=200)
        mock_event_response.json.return_value = event_res
        self.mock_init.auth = _test_auth_dict
        get_event_mock.return_value = mock_event_response
        mock_event_request = self.mock_init.get_event('evt_6268bfc6f33cac0cfa54ab0a84a14928')
        self.assertEqual(mock_event_request.tradeables[0].name, 'Luka Doncic')
        self.assertIsInstance(mock_event_request, objects.Event)
        self.assertIsInstance(mock_event_request.games[0], objects.Game)
        self.assertIsInstance(mock_event_request.tradeables[0].entity, objects.Entity)

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_entry(self, get_entry_mock):
        mock_entry_response = mock.Mock(status_code=200)
        mock_entry_response.json.return_value = entry_res
        self.mock_init.auth = _test_auth_dict
        get_entry_mock.return_value = mock_entry_response

        mock_entry_request = self.mock_init.get_entries()

        self.assertEqual(mock_entry_request[0].profit, entry_res['entries'][0]['leaderboard']['amount'])

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_entities(self, get_entities_mock):
        mock_entities_response = mock.Mock(status_code=200)
        mock_entities_response.json.return_value = entities_res
        self.mock_init.auth = _test_auth_dict
        get_entities_mock.return_value = mock_entities_response

        mock_entities_request = self.mock_init.get_entities()

        self.assertIsInstance(mock_entities_request[0].team, objects.Team)
        self.assertEqual(mock_entities_request[0].name, 'Kevin Durant')

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_game_logs(self, get_game_logs_mock):
        mock_game_log_response = mock.Mock(status_code=200)
        mock_game_log_response.json.return_value = game_logs_res
        self.mock_init.auth = _test_auth_dict
        get_game_logs_mock.return_value = mock_game_log_response

        mock_game_log_request = self.mock_init.get_game_logs(include_ent=True, include_game=True, include_team=True)

        self.assertIsInstance(mock_game_log_request[0], objects.GameLog)
        self.assertIsInstance(mock_game_log_request[15].entity, objects.Entity)
        self.assertIsInstance(mock_game_log_request[15].game, objects.Game)
        self.assertIsInstance(mock_game_log_request[15].team, objects.Team)

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_orders(self, get_orders_mock):
        mock_orders_response = mock.Mock(status_code=200)
        mock_orders_response.json.return_value = orders_res
        get_orders_mock.return_value = mock_orders_response
        self.mock_init.auth = _test_auth_dict

        mock_orders_request = self.mock_init.get_orders()

        self.assertIsInstance(mock_orders_request[0], objects.Order)
        self.assertEqual(mock_orders_request[2].tradeable_id, objects.Order(orders_res['orders'][2]).tradeable_id)

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_positions(self, get_positions_mock):
        mock_positions_response = mock.Mock(status_code=200)
        mock_positions_response.json.return_value = position_res
        get_positions_mock.return_value = mock_positions_response
        self.mock_init.auth = _test_auth_dict

        mock_positions_request = self.mock_init.get_positions()

        self.assertIsInstance(mock_positions_request[0], objects.Position)
        self.assertEqual(mock_positions_request[0].cost_basis_all_time,
                         position_res['positions'][0]['cost_basis_all_time'])

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_games(self, get_games_mock):
        mock_games_response = mock.Mock(status_code=200)
        mock_games_response.json.return_value = games_res
        get_games_mock.return_value = mock_games_response
        self.mock_init.auth = _test_auth_dict

        mock_games_request = self.mock_init.get_games()

        self.assertIsInstance(mock_games_request[0], objects.Game)
        self.assertEqual(mock_games_request[0].venue, games_res['games'][0]['venue'])

    @mock.patch('jockmkt_sdk.client.requests.get')
    def test_get_account_activity(self, get_account_activity_mock):
        mock_aact_response = mock.Mock(status_code=200)
        mock_aact_response.json.return_value = account_activity_res
        get_account_activity_mock.return_value = mock_aact_response
        self.mock_init.auth = _test_auth_dict

        mock_aact_request = self.mock_init.get_account_activity()
        print(mock_aact_request)

        self.assertIsInstance(mock_aact_request[0], objects.AccountActivity)
        self.assertIsInstance(mock_aact_request[0].order, objects.Order)
        self.assertIsInstance(mock_aact_request[0].order.tradeable, objects.Tradeable)
        self.assertIsInstance(mock_aact_request[0].order.entity, objects.Entity)
        self.assertIsInstance(mock_aact_request[0].order.event, objects.Event)
