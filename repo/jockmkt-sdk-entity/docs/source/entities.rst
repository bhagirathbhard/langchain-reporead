===========================
Entities & Entity Endpoints
===========================

.. entity endpoints_

Entity Endpoints:
=================

.. currentmodule:: jockmkt_sdk.client

.. automethod:: Client.get_entities

.. automethod:: Client.get_entity

.. code-block:: python

    entities = client.get_entities()
    entity = client.get_entity(entity_id="en_6025693d374b384994316c1e13f40416")

These methods return league-specific entity objects. get_entities returns a list of them, get_entity returns information
about one specific entity.

.. code-block:: python

    for entity in entities:
        print(entity)

Returns:
* an :class:`objects.Entity` object, which is then filtered to their specific league.

.. entity objects_

Entity Objects
==============

.. currentmodule:: jockmkt_sdk.objects

*All entities contain the following information:*

.. autoclass:: Entity

.. autoclass:: NBAEntity

.. autoclass:: NFLEntity

.. autoclass:: NHLEntity

.. autoclass:: PGAEntity

.. autoclass:: NASCAREntity

.. autoclass:: MLBEntity



