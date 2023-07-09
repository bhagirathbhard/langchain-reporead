from datetime import datetime, timedelta


class JockAPIException(Exception):
    """
    code -- type -- explanation
    400 -- bad_request -- required parameter not included or typo in required parameter
    401 -- not_authorized -- token is not valid; expired or keys not functioning
    402 -- request_failed -- event status error, user has not joined event, insufficient funds
    404 -- not_found -- incorrect api endpoint
    429 -- rate_limit -- max 10 orders (post, delete) per minute, max 250 other requests per minute. This limit resets
    at the beginning of every new clock minute (e.g 12:00:00, 12:01:00)
    50x -- internal_error -- request failed due to platform or network error. This SDK will automatically retry 3 times.
    """

    def __init__(self, response):
        now = datetime.now().strftime("%I:%M")
        rate_limit_reset = (datetime.now() + timedelta(minutes=1)).strftime("%I:%M")
        _error_dict = {
            'bad_request': "try fixing your parameters, or check if you're missing one!",
            'not_authorized': 'Double check your secret keys, or that your auth token is valid',
            'event_status': "Please wait for the market to open, or check that you're attempting to trade in an event \
                            that is currently open",
            'invalid_entry': 'Please join this event before attempting to trade!',
            'not_found': '',
            'rate_limit': 'You have placed too many requests since {}. Please wait until {}.'.format(
                now, rate_limit_reset),
            'request_failed': 'You have already entered the event or deleted your order',
            'bad_gateway': 'Maxmimum attempts made to resource with no valid response.\
                                 Check your network or try again later.',
            'insufficient_funds': 'You have insufficient funds available for this order.',
            'mixed_position': 'Close out your current position before placing this order.'
        }
        self.code = ""
        self.message = 'unknown error'
        self.helper = ''
        try:
            json_res = response.json()
        except ValueError:
            self.message = response.content
        else:
            print(json_res)
            if 'error' in json_res:

                self.code = json_res['error']
                self.message = json_res['message']
                self.helper = _error_dict[json_res['error']]

    def __str__(self):
        return 'JockAPIException {}: {} \n{}'.format(self.code, self.message, self.helper)

# class JockInputException(Exception):
#     _LEAGUES = []
#     _LEN_API_KEY = 23
#     _LEN_SECRET = 32
#     _LEN_IDS = 37
#
#     def __init__(self, **kwargs):
#         self.input_league = kwargs.get('league')
