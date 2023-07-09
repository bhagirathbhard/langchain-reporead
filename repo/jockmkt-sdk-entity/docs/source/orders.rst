======
Orders
======

.. order endpoints_

Order Endpoints
===============

.. currentmodule:: jockmkt_sdk.client

.. important::

    The user is limited to 10 orders per minute, with a refresh at the start of each new minute. The SDK will automatically handle this.

.. automethod:: Client.place_order

**Example:**

.. code-block:: python

    tradeable = client.get_event_tradeables(event_id)[0] #the first tradeable in the list
    client.place_order(id=tradeable.id, price=5, side='buy', phase='ipo', order_size=50)
    # Side must either be 'buy' or 'sell'
    # Phase must either be 'live' or 'ipo'
    # param qty is an int, number of shares the user wants to buy
    # OR order_size is an int, max amount of money the user wants to spend
    # such that: quantity = order_size // price

Raises error if the tradeable id is incorrect, or if the user hits the rate limit

Returns status of the order being placed

.. automethod:: Client.get_orders

Returns a list of :class:`objects.Order` objects

.. automethod:: Client.get_order

Returns a single :class:`objects.Order`

.. automethod:: Client.delete_order

Can only be used if the order was placed during live trading. Will return information about whether the cancellation was successful

.. order object_

Order Objects
=============

.. currentmodule:: jockmkt_sdk.objects

.. autoclass:: Order

.. autoclass:: PublicOrder

.. autoclass:: Trade