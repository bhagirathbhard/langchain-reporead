def _case_switch_ent(entity: dict):
    """
    case switching for entity responses -- there is significant variation between entities & their data
    """
    entity_type_dict = {
        'nba': NBAEntity,
        'nfl': NFLEntity,
        'nhl': NHLEntity,
        'pga': PGAEntity,
        'mlb': MLBEntity,
        'nascar': NASCAREntity,
        'simulated_horse_racing': Entity
    }

    return entity_type_dict[entity['league']](entity)
    # Previous case switching logic, not working in python < 3.10
    # match entity['league']:
    #     case 'nba':
    #         return NBAEntity(entity)
    #     case 'nfl':
    #         return NFLEntity(entity)
    #     case 'nhl':
    #         return NHLEntity(entity)
    #     case 'pga':
    #         return PGAEntity(entity)
    #     case 'mlb':
    #         return MLBEntity(entity)
    #     case 'nascar':
    #         return NASCAREntity(entity)


class Entity(object):
    """
    parent class for all entity objects, containing all universal fields shared between entity types

    the user can print any entity object via print(entity) -- see docs for information regarding responses

    :ivar entity_id:    the entity's ID, which can be used to search for a specific entity's information
    :ivar league:       the league in which the entity plays
    :ivar name:         the entity's full name
    :ivar first_name:   the entity's first name
    :ivar last_name:    the entity's last name
    :ivar updated_at:   when the entity was last updated
    :ivar news:         a dict containing news related to the entity
    """
    def __init__(self, entity: dict):
        self._populate_universal_fields(entity)

    def _populate_universal_fields(self, entity):
        self.entity_id = entity.get('id')
        self.league = entity.get('league')
        self.name = entity.get('name')
        self.first_name = entity.get('first_name')
        self.last_name = entity.get('last_name')
        self.updated_at = entity.get('updated_at')
        self.image_url = entity.get('image_url')
        self.news = entity.get('latest_news', {})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'


class NBAEntity(Entity):
    """
    NBA-specific entity data

    :ivar team_id:        the entity's team_id for use collecting team info
    :ivar team:           a dict containing team-related information
    :ivar preferred_name: player's preferred name
    :ivar position:       player's position
    :ivar height:         player's height
    :ivar weight:         player's weight
    :ivar jersey_number:  player's jersey number
    :ivar college:        player's college
    :ivar birthdate:      player's birthdate
    :ivar rookie_year:    player's rookie year
    :ivar status:         whether the player is currently active
    :ivar injury_status:  player's current injury status (day-to-day, injured reserve, etc.)
    :ivar injury_type:    type of injury (concussion, knee, etc.)
    """
    def __init__(self, entity):
        super().__init__(entity)
        self.team_id = entity.get('current_team_id')
        team = entity.get('team', {})  # turn this into a Team object, and do so for all team sports
        self.team = Team(team)
        self.preferred_name = entity.get('preferred_name')
        self.position = entity.get('position')
        self.height = entity.get('height')
        self.weight = entity.get('weight')
        self.jersey_number = entity.get('jersey_number')
        self.college = entity.get('college')
        self.birthdate = entity.get('birthdate')
        self.rookie_year = entity.get('rookie_year')
        self.status = entity.get('status')
        injury = entity.get('injury', {})
        self.injury_status = injury.get('status')
        self.injury_type = injury.get('type')


class NFLEntity(Entity):
    """
    NFL-specific entity data

    :ivar team_id:        the entity's team_id for use collecting team info
    :ivar team:           a dict containing team-related information
    :ivar preferred_name: player's preferred name
    :ivar position:       player's position
    :ivar height:         player's height
    :ivar weight:         player's weight
    :ivar jersey_number:  player's jersey number
    :ivar college:        player's college
    :ivar birthdate:      player's birthdate
    :ivar rookie_year:    player's rookie year
    :ivar status:         whether the player is currently active
    :ivar injury_status:  player's current injury status (day-to-day, injured reserve, etc.)
    :ivar injury_type:    type of injury (concussion, knee, etc.)
    """
    def __init__(self, entity):
        super().__init__(entity)
        self.team_id = entity.get('current_team_id')
        team = entity.get('team', {})
        self.team = Team(team)
        self.preferred_name = entity.get('preferred_name')
        self.position = entity.get('position')
        self.height = entity.get('height')
        self.weight = entity.get('weight')
        self.jersey_number = entity.get('jersey_number')
        self.college = entity.get('college')
        self.birthdate = entity.get('birthdate')
        self.rookie_year = entity.get('rookie_year')
        self.status = entity.get('status')
        injury = entity.get('injury', {})
        self.injury_status = injury.get('status')
        self.injury_type = injury.get('type')


class NASCAREntity(Entity):
    """
    Nascar-specific entity data

    :ivar team_id:         the entity's team_id for use collecting team info
    :ivar team:            a dict containing team-related information
    :ivar points_eligible: is the driver eligible to score points
    :ivar in_chase:        is the driver in the chase
    :ivar cars:            a list of cars that the driver races
    :ivar birthday:        driver's birthday
    :ivar birthplace:      where the driver was born
    :ivar rookie_year:     when did the driver first start racing
    :ivar status:          is the driver active or inactive
    :ivar injury_status:   is driver in, out or questionable (day-to-day, etc.)
    :ivar injury_type:     type of injury the driver is experiencing

    """
    def __init__(self, entity):
        super().__init__(entity)
        self.team_id = entity.get('current_team_id')
        team = entity.get('team', {})
        self.team = Team(team)
        self.points_eligible = entity.get('points_eligible', False)
        self.in_chase = entity.get('in_chase', False)
        self.cars = entity.get("cars", [])
        self.birthday = entity.get('birthday')
        self.birthplace = entity.get('birth_place')
        self.rookie_year = entity.get('rookie_year')
        self.status = entity.get('status')
        injury = entity.get('injury', {})
        self.injury_status = injury.get('status')
        self.injury_type = injury.get('type')


class NHLEntity(Entity):
    """
    NHL-specific entity data

    :ivar team_id:        the entity's team_id for use collecting team info
    :ivar team:           a dict containing team-related information
    :ivar preferred_name: player's preferred name
    :ivar position:       player's position
    :ivar height:         player's height
    :ivar weight:         player's weight
    :ivar jersey_number:  player's jersey number
    :ivar handedness:     is the player right or left-handed
    :ivar rookie_year:    player's rookie year
    :ivar status:         whether the player is currently active
    :ivar injury_status:  player's current injury status (day-to-day, injured reserve, etc.)
    :ivar injury_type:    type of injury (concussion, knee, etc.)
    """
    def __init__(self, entity):
        super().__init__(entity)
        self.team_id = entity.get('current_team_id')
        team = entity.get('team', {})
        self.team = Team(team)
        self.preferred_name = entity.get('preferred_name')
        self.position = entity.get('position')
        self.height = entity.get('height')
        self.weight = entity.get('weight')
        self.jersey_number = entity.get('jersey_number')
        self.handedness = entity.get('handedness')
        self.rookie_year = entity.get('rookie_year')
        self.status = entity.get('status')
        injury = entity.get('injury', {})
        self.injury_status = injury.get('status')
        self.injury_type = injury.get('type')


class PGAEntity(Entity):
    """
    PGA-specific entity data

    :ivar preferred_name: player's preferred name
    :ivar birthday:       player's birthday
    :ivar height:         player's height
    :ivar weight:         player's weight
    :ivar college:        player's attended college - not applicable to international players
    :ivar rookie_year:    player's rookie year
    :ivar country:        player's country of origin
    :ivar injury_status:  player's current injury status (day-to-day, injured reserve, etc.)
    :ivar injury_type:    type of injury (concussion, knee, etc.)
    """
    def __init__(self, entity):
        super().__init__(entity)
        self.preferred_name = entity.get('preferred_name')
        birthday = entity.get('birthdate', None)
        if birthday is not None:
            self.birthdate = birthday[:10]
        else:
            self.birthdate = birthday
        self.height = entity.get('height')
        self.weight = entity.get('weight')
        self.college = entity.get('college')
        self.rookie_year = entity.get('turned_pro')
        self.country = entity.get('country')
        injury = entity.get('injury', {})
        self.injury_status = injury.get('status')
        self.injury_type = injury.get('type')


class MLBEntity(Entity):
    """
    MLB-specific entity data

    :ivar team_id:        the entity's team_id for use collecting team info
    :ivar team:           a dict containing team-related information
    :ivar preferred_name: player's preferred name
    :ivar position:       player's position
    :ivar jersey_number:  player's jersey number
    :ivar college:        player's alma mater
    :ivar debut:          player's rookie year and date
    :ivar status:         whether the player is currently active
    :ivar birthdate:      player's birthdate
    :ivar injury_status:  player's current injury status (day-to-day, injured reserve, etc.)
    :ivar injury_type:    type of injury (concussion, knee, etc.)
    """
    def __init__(self, entity):
        super().__init__(entity)
        self.team_id = entity.get('current_team_id')
        team = entity.get('team', {})
        self.team = Team(team)
        self.preferred_name = entity.get('preferred_name')
        self.position = entity.get('position')
        self.jersey_number = entity.get('jersey_number')
        self.college = entity.get('college')
        self.debut = entity.get('debut')
        self.status = entity.get('status')
        self.birthdate = entity.get('birthdate')
        injury = entity.get('injury', {})
        self.injury_status = injury.get('status')
        self.injury_type = injury.get('type')


class Team(object):
    """
    Team object containing team-related attributes, such as: team_id, location, name, league and abbreviation

    user can call instance.available_attributes to see what instance variables are available.

    :ivar team_id:      the team's Jock MKT identifier
    :ivar location:     home city for the team (e.g. Los Angeles, New York, etc.)
    :ivar name:         team's name (e.g. Lakers, 49ers, etc.)
    :ivar league:       which league the team is a part of (e.g. nfl, nhl, etc.)
    :ivar abbreviation: shortened team name (e.g. LAL, SF, BKN, etc.)
    """
    def __init__(self, team):
        self.team_id = team.get('id')
        self.location = team.get('location')
        self.name = team.get('name')
        self.league = team.get('league')
        self.abbreviation = team.get('abbreviation')

    def available_attributes(self):
        """user can call self.available_attributes to see what instance variables are available for that instance of the
        class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'


class Game(object):
    """
    Games differ significantly, and you can expect significantly different information under "state" depending on the
    league. See docs for more info, or use self.print_game to get an idea of what the keys are.

    use Game.available_attributes to see available attributes.

    :ivar game_id:          Jock MKT's id for this game
    :ivar game_name:        game's name (e.g. Lakers vs Warriors)
    :ivar league:           which league the game applies to
    :ivar start:            what time the game is supposed to start
    :ivar venue:            a dict containing venue location, such as whether it is to be played outdoors or venue name
    :ivar status:           is the game scheduled, in_progress or final
    :ivar amount_completed: percentage of the game that has been completed
    :ivar state:            a dict containing information such as the clock, period/quarter/inning, length, etc.
    :ivar weather:          information about the weather, only applies to some sports & outdoor venues
    :ivar home_info:        information about the home team, such as score, runs, hits, etc.
    :ivar away_info:        information about the away team, such as score, runs, hits, etc.
    """

    def __init__(self, game: dict):
        self.game_id = game.get('id')
        self.game_name = game.get('name')
        self.league = game.get('league')
        self.start = game.get('scheduled_start')
        self.venue = game.get('venue')
        self.status = game.get('status')
        self.amount_completed = game.get('amount_completed')
        self.state = game.get('state')
        self.weather = game.get('weather')
        self.home_info = game.get('home', {})
        self.away_info = game.get('away', {})

    # def _populate_team_info(self, game: dict):
    #     home = game.get('home', {})
    #     for key in home:
    #         self.__dict__['home_' + key] = home[key]
    #     away = game.get('away', {})
    #     for key in away:
    #         self.__dict__['away_' + key] = away[key]

    def available_attributes(self):
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'


class GameLog(object):
    """
    different leagues will return different dictionaries of stats/projected. There is currently no league identifier.

    use GameLog.available_attributes() to see what attributes can be called.

    :ivar id:              Jock MKT's unique identifier for this game log
    :ivar entity_id:       entity_id for the player to which this game log applies
    :ivar game_id:         game_id to which this game log applies
    :ivar team_id:         team that this player is one
    :ivar scheduled_start: time that the game was scheduled to start
    :ivar updated_at:      when this log was last updated
    :ivar projected_stats: a dictionary of stat projections, which will be unique for each league
    :ivar actual_stats:    a dictionary of actual, scored stats, unique by league
    :ivar league:          league to which this game log applies
    :ivar entity:          :class:`objects.Entity` information about the entity to which this log applies
    :ivar game:            :class:`objects.Game` information about the game to which this log applies
    :ivar team:            :class:`objects.Team` information about the team this player is on
    """

    def __init__(self, game_log: dict):
        self.id = game_log.get('id')
        self.entity_id = game_log.get('entity_id')
        self.game_id = game_log.get('game_id')
        self.team_id = game_log.get('team_id')
        self.scheduled_start = game_log.get('scheduled_start')
        self.updated_at = game_log.get('updated_at')
        projected_stats = game_log.get('projected_stats', {'league': None})
        self.projected_stats = projected_stats
        actual_stats = game_log.get('stats', {'league': None})
        self.actual_stats = actual_stats
        self.league = actual_stats.get('league', projected_stats.get('league'))
        entity = game_log.get('entity', {'league': self.league})
        self.entity = _case_switch_ent(entity)
        game = game_log.get('game', {})
        self.game = Game(game)
        team = game_log.get('team', {})
        self.team = Team(team)

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'

#

class Event(object):
    """
    Class dedicated to storing event-related info. May contain list of Game objects, Tradeable objects and other
    information related to payouts and whether the event is a contest.

    :ivar event_id:      event_id for the chosen event, accessed via self.event_id. Used to access other event-specific info
    :ivar name:          the event's name as displayed on the app
    :ivar description:   the event's description
    :ivar type:          the type of event, either a contest or a cash market
    :ivar status:        the event's status. One of: scheduled, cancelled, halted, ipo, ipo_closed, live, live_closed, payouts_completed, prizes_paid or contests_paid
    :ivar league:        the league to which this event's scoring, games and players apply
    :ivar ipo_start:     timestamp at which the ipo opens
    :ivar ipo_end:       estimated time at which the ipo should end
    :ivar est_close:     estimated time the event will close
    :ivar amt_completed: percentage of the event completed
    :ivar updated_at:    last timestamp at which the event was updated
    :ivar payouts:       a list of payouts for the event in the following format: 'payouts': [{'position': 1, 'amount': 25},..., {'position': n, 'amount': k}]
    :ivar games:         a list of :class:`objects.Game` objects
    :ivar tradeables:    a list of :class`objects.Tradeable` objects
    :ivar contest:       information about the contest, if it's a contest-type market see: `objects.Event.type`
    :ivar share_count:   the number of shares available for that market
    """
    def __init__(self, event: dict):
        self.event_id = event.get('id')
        self.name = event.get('name')
        self.description = event.get('description')
        self.type = event.get('type')
        self.status = event.get('status')
        self.league = event.get('league')
        self.ipo_start = event.get('ipo_open_at')
        self.ipo_end = event.get('live_at_estimated')
        self.est_close = event.get('close_at_estimated')
        self.amt_completed = event.get('amount_completed')
        self.amount_completed = event.get('amount_completed')
        self.updated_at = event.get('updated_at')
        self.payouts = event.get('payouts', [])
        self.current_shares = event.get('current_shares')
        games = event.get('games', {})
        self.games = []
        for game in games:
            self.games.append(Game(game))
        tradeables = event.get('tradeables', {})
        self.tradeables = []
        for tdbl in tradeables:
            self.tradeables.append(Tradeable(tdbl))
        self.contest = event.get('contest', {})

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + "\n"


class Tradeable(object):
    """
    object containing information about an event-specific tradeable object, including prices and projections

    :ivar tradeable_id:      this entity's event-specific identifier, used to place orders
    :ivar league:            league this entity participates in
    :ivar updated_at:        when this tradeable was last updated
    :ivar entity_id:         the entity's unique identifier, event-agnostic
    :ivar event_id:          event to which this tradeable_id applies
    :ivar game_id:           game to which this tradeable applies
    :ivar next_game_id:      only exists when there's a double header in MLB - player's next game
    :ivar projected_games_remaining: how many games the player has left to play in this slate (exclusive to MLB double headers)
    :ivar projected_games_total: total number of games the player will play in this slate (exclusive to MLB double headers)
    :ivar fpts_proj_pregame: the tradeable's pregame projected fantasy points
    :ivar fpts_proj_live:    tradeable's live projected fantasy points
    :ivar fpts_scored:       tradeable's fantasy points scored
    :ivar ipo:               price at which the tradeable IPOs. Will be None if the event status is not "live",
                             "live_closed", or "payouts_completed
    :ivar high:              the highest price at which this tradeable was traded
    :ivar low:               lowest traded price
    :ivar last:              last traded price
    :ivar estimated:         Jock MKT's estimated price
    :ivar bid:               highest active bid
    :ivar ask:               lowest active ask
    :ivar final:             final payout
    :ivar stats:             a list or dict of applicable statistics
    :ivar name:              the player's name
    :ivar entity:            :class:`object.Entity` object containing entity info
    """
    def __init__(self, tradeable: dict):
        self.tradeable_id = tradeable.get('id')
        self.updated_at = tradeable.get('updated_at')
        self.league = tradeable.get('league')
        self.entity_id = tradeable.get('entity_id')
        self.event_id = tradeable.get('event_id')
        self.game_id = tradeable.get('focus_game_id')
        self.next_game_id = tradeable.get('next_game_id')
        self.games_remaining = tradeable.get('projected_games_remaining')
        self.total_games = tradeable.get('projected_games_total')
        points = tradeable.get('points', {})
        self.fpts_proj_pregame = points.get('projected')
        self.fpts_proj_live = points.get('projected_live')
        self.fpts_scored = points.get('scored')
        price = tradeable.get('price', {})
        self.ipo = price.get('ipo', 1)
        self.high = price.get('high')
        self.low = price.get('low')
        self.last = price.get('last')
        self.estimated = price.get('estimated')
        self.bid = price.get('bid')
        self.ask = price.get('ask')
        self.final = price.get('final')
        ranks = tradeable.get('rank')
        self.rank_proj_pregame = ranks.get('projected')
        self.rank_proj_live = ranks.get('projected_live')
        self.rank_scored = ranks.get('scored')
        self.rank_price = ranks.get('price')
        self.rank_final = ranks.get('final')
        self.stats = tradeable.get('stats', {})
        # if type(stats) != dict and len(stats) > 0:
        #     for key in stats[0]:
        #         self.__dict__[key] = stats[0][key]
        # else:
        #     for key in stats:
        #         self.__dict__[key] = stats[key]
        entity = tradeable.get('entity', {'league': tradeable['league']})
        self.name = entity.get('name')
        self.image = entity.get('image_url')
        self.entity = _case_switch_ent(entity)

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'


class Entry(object):
    """object containing information about a user's entry into an event, such as profit, leaderboard position

    :ivar entry_id:         the entry's identifier
    :ivar event_id:         the event's identifier
    :ivar leaderboard_pos:  the user's leaderboard position
    :ivar profit:           the user's profit in this entry, not including fees
    :ivar updated_at:       when this entry was last updated
    :ivar favorites:        a list of favorited tradeables
    :ivar event:            :class:`objects.Event` object containing event specific information
    :ivar payouts:          after the event is finished, a list of payouts made to the user for their holdings
    """
    def __init__(self, entry: dict):
        self.entry_id = entry.get('id')
        self.event_id = entry.get('event_id')
        leaderboard = entry.get('leaderboard')
        self.leaderboard_pos = leaderboard.get('position')
        self.profit = leaderboard.get('amount')
        self.updated_at = entry.get('updated_at')
        self.favorites = entry.get('favorites', [])  # interact this with tradeable lookup
        event = entry.get('event', {})
        self.event = Event(event)
        self.payouts = entry.get('payouts')

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'


class Position(object):
    """an object containing information about open positions or holdings. Note that instance variables do not
    include fees

    :ivar tradeable_id:        the player's tradeable_id for the position
    :ivar event_id:            identifier for the event to which the position applies
    :ivar sold_count:          total quantity sold over the course of the event
    :ivar bought_count:        total quantity purchased over the course of the event
    :ivar buy_interest:        amount of shares the user is currently trying to buy
    :ivar sell_interest:       amount of shares the user is currently trying to sell
    :ivar quantity_owned:      number of shares the user owns
    :ivar cost_basis:          total amount spent on shares of the player that the user currently owns
    :ivar proceeds:            total amount of income for open position
    :ivar cost_basis_all_time: total amount spent on shares of the player whether they are currently owned or not
    :ivar proceeds_all_time:   total realized profit and loss for selling shares of this tradeable
    """
    def __init__(self, position: dict):
        self.tradeable_id = position.get('tradeable_id')
        self.event_id = position.get('event_id')
        self.bought_count = position.get('bought_count')
        self.sold_count = position.get('sold_count')
        self.buy_interest = position.get('buy_interest')
        self.sell_interest = position.get('sell_interest')
        self.quantity_owned = position.get('quantity')
        self.cost_basis = position.get('cost_basis')
        self.proceeds = position.get('proceeds')
        self.cost_basis_all_time = position.get('cost_basis_all_time')
        self.proceeds_all_time = position.get("proceeds_all_time")
        self.updated_at = position.get('updated_at')

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'


class Order(object):
    """
    object dedicated to storing information about orders that the user has placed

    :ivar account:         The account associated with the order, only available from event_activity endpoint from ws feed.
    :ivar order_id:        the order's specific identification
    :ivar tradeable_id:    the tradeable that the order was placed for
    :ivar entity_id:       the underlying entity_id for which the order was placed
    :ivar event_id:        the event in which the order was placed
    :ivar status:          current status, one of: created, accepted, filled, outbid, cancelled, or expired
    :ivar side:            side of the order (buy or sell)
    :ivar phase:           phase during which the order was placed (live or ipo)
    :ivar quantity:         amount of shares the user wants to buy
    :ivar limit_price:     the price the user specified in their order
    :ivar cost_basis:      how much the user spent on shares (only present on buy orders)
    :ivar fee_paid:        sum of fees paid for the order
    :ivar proceeds:        how much the user received for their sell order (if it was a sell order)
    :ivar filled_quantity: quantity of shares that have been filled,
    :ivar created_at:      timestamp at which the order was created
    :ivar accepted_at:     timestamp at which the order was accepted
    :ivar updated_at:      timestamp at which the order last updated (some shares bought or sold)
    :ivar filled_at:       time at which the order was completely filled
    :ivar cancellation_requested_at: when a cancellation was requested
    """
    def __init__(self, order: dict):
        account = order.get('account', {})
        self.account = account
        self.order_id = order.get('id')
        self.tradeable_id = order.get('tradeable_id')
        self.entity_id = order.get('entity_id')
        self.event_id = order.get('event_id')
        self.status = order.get('status')
        self.side = order.get('side')
        self.type = order.get('type')
        self.phase = order.get('phase')
        self.direction = order.get('direction')
        self.time_in_force = order.get('time_in_force')
        self.quantity = order.get('quantity')
        self.limit_price = order.get('limit_price')
        self.cost_basis = order.get('cost_basis', 0)
        self.fee_paid = order.get('fee_paid', 0)
        self.proceeds = order.get('proceeds', 0)
        self.filled_quantity = order.get('filled_quantity', 0)
        tradeable = order.get('tradeable', {})
        if len(tradeable) > 0:
            self.tradeable = Tradeable(tradeable)
        entity = order.get('entity', {})
        if len(entity) > 0:
            self.entity = _case_switch_ent(entity)
        event = order.get('event', {})
        if len(event) > 0:
            self.event = Event(event)
        self.created_at = order.get('created_at')
        self.accepted_at = order.get('accepted_at')
        self.updated_at = order.get('updated_at')
        self.filled_at = order.get('filled_at')
        self.cancellation_requested_at = order.get('cancellation_requested_at')

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'

class PublicOrder(object):
    """
    Public order object for use with websockets

    :ivar user_id:      the user's unique identifier
    :ivar user_tags:    the user's tags (if they are a marketmaker, etc.)
    :ivar username:     the user's display name
    :ivar member_since: when the user joined
    :ivar event_id:     the event id to which this order applies
    :ivar tradeable_id: the player who is being traded's event-specific id
    :ivar entity_id:    the player's global JM identifier
    :ivar side:         the side of the order (buy or sell)
    :ivar phase:        the phase in which the order was placed (ipo or live)
    :ivar created_at:   when the order was created
    """

    def __init__(self, order: dict):
        account = order.get('account', {})
        self.user_id = account.get('id')
        self.user_tags = account.get('tags')
        self.username = account.get('display_name')
        self.member_since = account.get('created_at')
        self.order_id = order.get('id')
        self.event_id = order.get('event_id')
        self.tradeable_id = order.get('tradeable_id')
        self.entity_id = order.get('entity_id')
        self.side = order.get('side')
        self.phase = order.get('phase')
        self.created_at = order.get('created_at')

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'

class Trade(object):
    """
    Public trade info including price and quantity. Available only with websockets.

    :ivar trade_id:      The id of the trade
    :ivar price:         The price at which the trade went through
    :ivar quantity:      The size of the trade
    :ivar tradeable_id:  The id of the player stock that was traded
    :ivar created_at:    Time at which the order went through
    """
    def __init__(self, trade):
        self.trade_id = trade.get('id')
        self.price = trade.get('price')
        self.quantity = trade.get('quantity')
        self.tradeable_id = trade.get('tradeable_id')
        self.created_at = trade.get('created_at')

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'


class AccountActivity(object):  # will need to get more advanced with the way aact objects are handled in future
    """object dedicated to all different kinds of account activity. There are numerous unique instance vars so the
    user should call self.available_attributes to see what instance vars are available"""
    def __init__(self, aact):
        for key in aact:
            if key == 'event':
                self.__dict__[key] = Event(aact[key])
            elif key == 'order':
                self.__dict__[key] = Order(aact[key])
            else:
                self.__dict__[key] = aact[key]

    def available_attributes(self):
        """
        The purpose of this method is to display the available instance variables so the user knows what they can access
        in each instance of the class
        """
        print({key for key in self.__dict__.keys()})

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'

class Balance(object):
    """
    Balance object

    :ivar currency:      the currency, either usd or contest-specific currency
    :ivar currency_type: currency type (either contest or fiat)
    :ivar event_id:      only available if contest
    :ivar total:         total available currency
    :ivar buying_power:  total currency available for trading
    :ivar pending:       any pending deposits
    """
    def __init__(self, balance):
        self.currency = balance.get('currency')
        self.currency_type = balance.get('type')
        if self.currency_type == 'contest' and not self.currency:
            self.event_id = 'evt_' + self.currency[4:]
        self.total = balance.get('total')
        self.buying_power = balance.get('buying_power')
        self.pending = balance.get('pending')

    def __repr__(self):
        return str(self.__dict__) + '\n'

    def __str__(self):
        return str(self.__dict__) + '\n'
