========
Examples
========

.. _examples:

.. important::

    The Jock MKT Api does not display all results for many of the endpoints by default. In order to display more results, the user has to implement pagination. It can be done so as follows:

.. pagination_

Paginating Results
==================

**any endpoint that has start and limit as keywords will require pagination**

.. code-block:: python
    :caption: paginating request results using for statement, generating a list of all NBA Entities.

    nba_entities = []
    for i in range(10):
        nba_entities.extend(client.get_entities(start=i, limit=100, league='nba'))

.. note::

    We use .extend rather than .append on the list so we are not appending new lists to a list, but generating one list of all nba entities.

.. rate limits_

Dealing with order rate limits
==============================

.. note::

    Since you are limited to 10 orders per minute, you must limit how you place orders.

.. code-block:: python

    from datetime import datetime
    import time

    #Option 1:
    for order in orders:
        client.place_order(tradeable_id, price, side, phase, qty)
        time.sleep(6)

    #Option 2:
    counter = 0
    for order in orders:
        client.place_order(tradeable_id, price, side, phase, qty)
        counter += 1

        if counter == 10:
            counter = 0
            time.sleep(60)

    #Option 3:
    counter = 0
    for order in orders:
        client.place_order(tradeable_id, price, side, phase, qty)
        counter += 1

        if counter == 10:
            counter = 0
            sleeptime = 60.1 - datetime.now().second
            time.sleep(sleeptime)
            print(sleeptime)


