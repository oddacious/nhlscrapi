

from nhlscrapi._tools import build_enum


EventType = build_enum('Event', 'ShotAttempt', 'Shot', 'Block', 'Miss', 'Goal',
    'Hit', 'FaceOff', 'Giveaway', 'Takeaway', 'Penalty', 'Stoppage', 'ShootOutAtt',
    'ShootOutGoal', 'PeriodEnd', 'GameEnd', 'ShootOutEnd')
"""Enum indicating event type."""


class Event(object):
    """Base class for event codes in the RTSS play-by-play reports"""

    def __init__(self, event_type = EventType.Event, desc = "", detailed_desc = "",
            full_date_time = None, coordinates = None, goals = None, team = None):
        self.event_type = event_type
        """The :py:class:`.EventType` enum values corresponding to the event."""
        self.desc = desc
        """The RTSS description of the play."""
        self.detailed_desc = detailed_desc
        """The detailed description of the play."""
        self.full_date_time = full_date_time
        """The full datetime of the play."""
        self.coordinates = coordinates
        """The coordinates of the play."""
        self.goals = goals
        """The current team goals of the play."""
        self.team = team
        """The team which performed the play."""
        self.abs_differential = None
        """The absolute goal differential at time of play."""
        self.close = None
        """Whether the game was close at time of play."""

    def supplement(self, detailed):
        """
        Update details of the event with information gathered from the JSON feed

        :returns: ``self`` on success, ``None`` otherwise
        """

        self.coordinates = detailed['coordinates']
        self.detailed_desc = detailed['result']['description']
        self.full_date_time = detailed['about']['dateTime']
        self.goals = detailed['about']['goals']

        # Some events are not tied to a specific team, such as GAME_SCHEDUED
        if 'team' in detailed:
            self.team = detailed['team']['name']

        if self.event_type == EventType.Goal and detailed['result']['event'] == "Goal":
            self.is_empty_net = detailed['result']['isEmptyNet']
            self.strength = detailed['result']['strength']['code']

        return self
        """
        game_seconds = min(3, max(0, p['period'] - 1)) * 20 * 60 + # Seconds in prior periods 
            int(time[0]) * 60 + # Current period minutes
            int(time[1]) +  # Current period seconds
            (p['period'] == 5) * 5 * 60 # Overtime minutes
        game_seconds = min(3, max(0, self.period - 1)) * 20*60 + \
            int(time[0]) * 60 + \
            int(time[1]) + \
            (self.period == 5) * 5 * 60
        """

    def calculate_differential(self):
        """
        Update the absolute differential and game close status, based on information retrieved from the JSON feed.
        Call supplement() first
        
        
        :returns: ``self`` on success, ``None`` otherwise
        """

        if self.goals is not None:
            self.abs_differential = abs(self.goals['home'] - self.goals['away'])
            self.close = abs_differential == 0 or (abs_differential <= 1 and self.game_seconds <= 2400)
            return self

        return None

class ShotAttempt(Event):
    def __init__(self, event_type = EventType.ShotAttempt):
        super(ShotAttempt, self).__init__(event_type)
        self.shooter = { 'team': '', 'name': '', 'num': 0 }
        """Shooter info ``{ 'team': team, 'name': name, 'num': num }``"""

        self.shot_type = ""
        """Description of shot, e.g. Wrist Shot, et c"""

        self.dist = 0
        """Distance of shot in feet"""

        self.is_penalty_shot = False
        """Flag indicating if it was a penalty shot"""


class Shot(ShotAttempt):
    def __init__(self):
        super(Shot, self).__init__(EventType.Shot)


class Goal(Shot):
    def __init__(self):
        super(Goal, self).__init__()
        self.event_type = EventType.Goal
        self.assists = []

        self.is_empty_net = False
        self.strength = None


class Miss(ShotAttempt):
    def __init__(self):
        super(Miss, self).__init__(EventType.Miss)


class Block(ShotAttempt):
    def __init__(self):
        super(Block, self).__init__(EventType.Block)


class Hit(Event):
    def __init__(self):
        super(Hit, self).__init__(EventType.Hit)


class FaceOff(Event):
    def __init__(self):
        super(FaceOff, self).__init__(EventType.FaceOff)


class Stoppage(Event):
    def __init__(self, event_type=EventType.Stoppage):
        super(Stoppage, self).__init__(event_type)


class PeriodEnd(Stoppage):
    def __init__(self):
        super(PeriodEnd, self).__init__(EventType.PeriodEnd)


class GameEnd(Stoppage):
    def __init__(self):
        super(GameEnd, self).__init__(EventType.GameEnd)


class ShootOutEnd(Stoppage):
    def __init__(self):
        super(ShootOutEnd, self).__init__(EventType.ShootOutEnd)


class Penalty(Event):
    def __init__(self):
        super(Penalty, self).__init__(EventType.Penalty)


class Turnover(Event):
    """Base class for Takeaway and Giveaway events. Not meant to be used directly"""
    class TOType:
        Takeaway = 0
        Giveaway = 1

    def __init__(self, to_type = TOType.Takeaway):
        self.to_type = to_type
        if to_type == Turnover.TOType.Giveaway:
            super(Turnover, self).__init__(EventType.Giveaway)
        else:
            super(Turnover, self).__init__(EventType.Takeaway)

    @property
    def turnover_type(self):
        return self._turnover_type

    @turnover_type.setter
    def turnover_type(self, value):
        if isinstance(value, TOType):
            self._turnover_type = value
        else:
            raise ValueError(str(value) + " is not of type Turnover.TOType")


class Takeaway(Turnover):
    def __init__(self):
        super(Takeaway, self).__init__(Turnover.TOType.Takeaway)


class Giveaway(Turnover):
    def __init__(self):
        super(Giveaway, self).__init__(Turnover.TOType.Giveaway)


# accumulators are based upon inheritance
# shoot outs don't count as a shot attempts
class ShootOutAtt(Event):
    def __init__(self, event_type = EventType.ShootOutAtt):
        super(ShootOutAtt, self).__init__(event_type)
        self.shooter = { 'team': '', 'name': '', 'num': 0 }
        self.shot_type = ""
        self.dist = 0


class ShootOutGoal(ShootOutAtt):
    def __init__(self):
        super(ShootOutGoal, self).__init__(EventType.ShootOutGoal)


def _get_class_hierarchy(base):
    l = [base]
    for t in base.__subclasses__():
        grandchildren = t.__subclasses__()
        if len(grandchildren) > 0:
            l.extend(_get_class_hierarchy(t))
        else:
            l.append(t)

    return l


class EventFactory(object):
    """
    Factory for creating event objects corresponding to the different types of plays (events) in RTSS play by play data.
    Constructor selected based upon the event enum :py:class:`.EventType.Events` passed.
    """

    event_list = _get_class_hierarchy(Event)
    """List of available events loaded dynamically by following the subclass structure of :py:class:`.Event`."""

    @staticmethod
    def Create(event_type):
        """
        Factory method creates objects derived from :py:class`.Event` with class name matching the :py:class`.EventType`.

        :param event_type: number for type of event
        :returns: constructed event corresponding to ``event_type``
        :rtype: :py:class:`.Event`
        """
        if event_type in EventType.Name:
            # unknown event type gets base class
            if EventType.Name[event_type] == Event.__name__:
                return Event()
            else:
                # instantiate Event subclass with same name as EventType name
                return [t for t in EventFactory.event_list if t.__name__ == EventType.Name[event_type]][0]()
        else:
            raise TypeError("EventFactory.Create: Invalid EventType")
