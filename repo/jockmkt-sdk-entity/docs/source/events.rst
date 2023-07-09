======
Events
======

.. events endpoints_

Event Endpoints
===============

.. currentmodule:: jockmkt_sdk.client

.. automethod:: Client.get_scoring

.. automethod:: Client.get_events

.. automethod:: Client.get_event

Recommended usage: pull a list of events using get_events and then get event-specific information using the event_id.

*Example*

.. code-block:: python

    events = client.get_events()
    event_info = client.get_event(event[0].event_id)

This will include information about event games, payouts and tradeables. You can also use the following methods to pull that data.

.. automethod:: Client.get_event_tradeables

returns a list of :class:`objects.Tradeable` objects. Tradeable ID is what is used to place orders.

.. automethod:: Client.get_event_payouts

returns a dictionary of event payouts.

.. automethod:: Client.get_event_games

returns a list of :class:`object.Game` objects


.. event objects_

Event Object
============

.. currentmodule:: jockmkt_sdk.objects

.. autoclass:: Event