=======
Account
=======
.. Account Balance_

The user should call call client.get_account_balance() to retreive balances. May in the future make this automatic.

it can be accessed as follows:

.. currentmodule:: jockmkt_sdk.client

.. code-block:: python

    client = Client(secret_key, api_key)
    client.get_account_balance()

    #you can access this information:

    print(client.balance)

.. Account Activity_

Account Activity data is a little bit different.

.. automethod:: Client.get_account_activity

.. code-block:: python

    account_activity = client.get_account_activity()

Returns a list of all account activity, including orders, payouts, event entries, deposits and withdrawals.

Some examples:

.. code-block:: python

    print(type(account_activity))
    for activity in account_activity:
        print(activity)

Returns:

    For example:

        Payout:

>>> {'id': 'aact_6247ed15ed7f8339ead03a510517512c',
>>>    'object': 'account_activity:payout',
>>>    'payouts': [{'tradeable_id': 'tdbl_62452742abe97c136151cae9313fed5d',
>>>                'quantity': 6,
>>>                'price': 1,
>>>                'cost_basis': 27,
>>>                'cost_basis_all_time': 27,
>>>                'proceeds_all_time': 6,
>>>                'tradeable': {objects.Tradeable}, ...]}

A payout is a list of all payouts and respective tradeables from a single event

    Order:

>>> {'id': 'aact_624878935119dbbb29858440504c989e',
>>>  'object': 'account_activity:order',
>>>  'order_id': 'ord_62487893677bd6fec00c68ed47d3a0e2',
>>>  'created_at': 1648916627064,
>>>  'order': {objects.Order}


For more information regarding different types of account activity, please see here:
    `Jock MKT API Account Activity Docs <https://docs.jockmkt.com/#accountactivity>`_
