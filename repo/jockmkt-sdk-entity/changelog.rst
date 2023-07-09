=======================
Changelog - jockmkt-sdk
=======================

This changelog will document all changes after and including release **0.2.0** of the Jockmkt-sdk API Wrapper.

Releases follow `semantic versioning <https://semver.org/spec/v2.0.0.html>`_.
The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_.

Docs available at: `Read The Docs <https://jockmkt-sdk.readthedocs.io/en/latest/>`_


Release 0.2.15
##############

``ADDED:``

- Option to include object count in your request.
    - If you are trying to get all of your orders, for example, you can set ``include_count=True`` in your request to return the total number of orders. Assists with pagination.
    - e.g.:

.. code-block:: python

    # The perfect number of requests to get all orders
    orders, order_count = client.get_orders(include_count=True)
    for i in range(order_count//100 + 1):
        orders.extend(client.get_orders(start=i)

- verbosity feature to get rid of print statements

``FIXED:``

- Typo in Entry docs
- Better self-documentation by renaming some variables within functions. Will not affect return values.
- Fixed key problem in NHL entity

Release 0.2.14
##############

``FIXED:``

- Deleted an annoying print statement.

Release 0.2.13
##############

``FIXED:``

- Typing issue

Release 0.2.12
##############

``FIXED``

- File structure problem

Release 0.2.11
##############

``FIXED``

- No longer raises an exception if the user has already joined an event.
- Now actually returns horse racing entities

``ADDED``

- New websocket connect method that should allow for a more graceful exit.

Release 0.2.10
##############

``FIXED:``

- Notifications from websockets not being pushed to messages
- Websocket messages not being converted to objects correctly

Release 0.2.9
#############

``FIXED:``

- Small incompatibility bug with | in typing

Release 0.2.8
#############

``ADDED:``

- Compatibility with earlier versions of python (>=3.7)

``FIXED:``

- Missing requirements in requirements.txt and pyproject.toml

Release 0.2.7
#############

``ADDED:``

- Added current_shares attribute to Event object
- ssl certification for websocket feed

0.2.6
#####

- added sold count to position object

Release 0.2.3 and 0.2.4
#############

``FIXED:``

- Decimal rounding error for pricing

- Github Actions


Release 0.2.2
#############

``Added:``

- Order response is now an Order object.
    - added direction and time_in_force instance variables

- Balance object

- 'insufficient_funds' and 'mixed_position' message in exception handling

- 'updated_at' attribute for Tradeable objects

``Fixed:``

- Order prices are now formatted using Decimal rather than ``"{0:.2f}".format()`` which was causing the occasional bug.

- ``.place_order()`` input typing was corrected

- Order object is correctly parsed from 'account' websocket endpoint

- kwargs are correctly unpacked in websocket error_handler

``Changed:``

- place_order args adjusted order of positional args:
    - tradeable_id, price, **qty: int = 1**, ...)
    - should not break any code

- Orders can now be placed like so (you do not need qty as a keyword argument):

```
client.place_order('tradeable_id', price, qty)
```


Release 0.2.1
#############

``Fixed:``

- Docs

- Event endpoint displaying only 20 results

Release 0.2.0
#############

``Added:``

- Functionality for websockets

``Fixed:``

- ``get_game_logs`` is now fully functional

- ``get_game_logs`` now includes ``statistics`` and ``projected_statistics`` attributes.

- order rate limit handling is fixed -- no order deletions will count towards the rate limit

Release 0.1.0
#############

``Added:``

- functionality for ALL Jockmkt API endpoints

- Automatically fetches an authorization token

- Objects for every relevant request: (i.e. tradeable, entity, event, order, etc.) that contain attributes for all available information.

- Rate limit handling for orders -- the user can place as many orders as they want and the SDK will automatically cache requests if they hit the limit

- Testing

- Event scoring information

- Full docstrings explaining every api request, return value and instance variable

- Full documentation with examples `here <https://jockmkt-sdk.readthedocs.io/en/latest/>`_






