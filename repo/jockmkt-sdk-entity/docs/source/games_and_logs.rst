=================
Games & Game Logs
=================

.. game endpoints_

Game Endpoints
==============

The purpose of these endpoints is to pull game-specific information, such as start times and status

.. currentmodule:: jockmkt_sdk.client

.. automethod:: Client.get_games

.. automethod:: Client.get_game

.. gamelog endpoints_

GameLog Endpoint
=================

Fetch player-specific game log from a single game, such as stats and projections

.. automethod:: Client.get_game_logs

.. game/gamelog objects_

Game and GameLog objects
========================

.. currentmodule:: jockmkt_sdk.objects

.. autoclass:: Game

.. autoclass:: GameLog