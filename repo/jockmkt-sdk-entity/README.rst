============
Jock MKT SDK
============

.. image:: https://img.shields.io/pypi/v/jockmkt-sdk?style=for-the-badge
  :target: https://pypi.python.org/pypi/jockmkt-sdk

.. image:: https://img.shields.io/github/license/nysugfx/jockmkt-sdk?style=for-the-badge
  :target: https://github.com/nysugfx/jockmkt-sdk/LICENSE.txt

.. image:: https://img.shields.io/pypi/pyversions/jockmkt-sdk?style=for-the-badge
  :target: https://pypi.python.org/pypi/jockmkt-sdk

.. image:: https://static.pepy.tech/badge/jockmkt-sdk
  :target: https://pepy.tech/project/jockmkt-sdk

This is an unofficial wrapper built to interface with the Jock MKT API.

*The developer of this sdk is in no way affiliated with Jock MKT -- please use at your own risk.*

The aim of this SDK is to build a host of easy-to-use tools for users to interact with the Jock MKT API. It includes every possible api call, every optional argument, and objects that organize all of their responses. In the future, additions will be made to further simplify these api calls with the addition of useful tools.

`JockMKT Official API Docs <https://docs.jockmkt.com/>`_

**Code snippet**

.. code-block:: python

    # the following code will buy $50 worth of shares for every player in an event
    # whose last traded price is less than the estimated price
    client = Client()
    client.get_auth_token(secret_key, api_key)
    event = client.get_event(event_id, include_tradeables=True)
    for tradeable in event.tradeables:
         if tradeable.last < tradeable.estimated:
             auth.place_order(tradeable.id, price=tradeable.estimated, size=50)


Installation (via PyPi)
-----------------------
.. code-block:: bash

    pip install jockmkt-sdk

`PyPi Link <https://pypi.org/project/jockmkt-sdk/0.1.2/>`_

Note: If you have problems installing, please ensure that you have updated pip and setuptools. If you still have trouble, please install requirements manually.

Contribute
-----------
  - Source: https://github.com/nysugfx/jockmkt-sdk
  - Issue Tracker: https://github.com/nysugfx/jockmkt-sdk/issues

Docs
----
  - `ReadTheDocs <https://jockmkt-sdk.readthedocs.io/en/latest/index.html>`_

Features
--------
- Calls for every API endpoint
- Exception handling
- Simple auth token generation & use
- Simple order placement


Getting Started
===============

Obviously, create an account at `jockmkt.com <jockmkt.com>`_

Contact developers@jockmkt.com for your auth keys

Authorization & basic calls:
  .. code:: python

    from jockmkt-sdk.client import Client
    api_key = '<jm_key_xxx>'
    secret_key = '<xxx>'

    client = Client(secret_key, api_key)

    #display the first 100 nba entities
    players = client.get_entities(start=0, league='nba')

    #get 25 recent and upcoming events:
    events = client.get_events()

    #get the last 500 events:
    fetchall_events = []
    for i in range(5):
         fetchall_events.append(client.get_events(start=i, limit=100))

    #get a single event:
    event_id = events[0].event_id
    event = client.get_event(event_id, include_tradeables=True)

    #join an event:
    entry = client.create_entry(event_id)

    #view event profit:
    print(entry.profit)

    #view event tradeables:
    tradeables = event.tradeables

    #pick a specific player and place an order during IPO phase at the Jock MKT estimated price:
    for player in tradeables:
         if player.name == 'Paul George':
              client.place_order(player.tradeable_id, player.estimated)

    #buy a specified $ amount worth of a player at the market price, during live trading:
    order = client.create_order(id=player.tradeable_id, price=player.ask,
         phase='live', order_size=100)

    #cancel order
    client.cancel_order(order['order']['id'])

Contact
-------
nysu.gfx@gmail.com
