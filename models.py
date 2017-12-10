import random
from enum import Enum

class Thing:
    '''A base class for all objects in the simulation.'''
    def __init__(self, name):
        '''
        :param name: The name of the thing.
        :type name: str
        '''
        self.name = name # type: str
    
    def __eq__(self, other):
        if not type(self) is type(other):
          return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
        
    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return self.name
        
class Object(Thing):
    '''An object during the simulation that can be found by characters.'''
    def __init__(self, name, location=None, owner=None):
        '''
        :param name: The name of the object.
        :type name: str
        :param location: The location of the object. Defaults to None.
        :type location: str
        :param owner: The character who owns the object or None if the object has no owner. Defaults to None.
        :type owner: Character
        '''
        Thing.__init__(self, name)
        #assert owner is None or isinstance(owner, Character)

        self.location = location # type: str
        self.owner = owner # type: Character

class Location(Thing):
    def __init__(self, name):
      Thing.__init__(self, name)

class Knowledge:
    def __init__(self, source, subject, action, target, timestamp, value = 0):
        # Knowledge format: SOURCE told me that SUBJECT performed ACTION on TARGET
        self.source = source # type: Character. Character that gave this information
        self.subject = subject # type: Character
        self.action = action # type: Actions
        self.target = target # type: Character
        self.timestamp = timestamp # type: int
        self.value = value # type: float. Auxillary numerical value, currently used with LIKES action to tell the value of relationship
        
    def equality_tuple(self):
        return (self.subject, self.action, self.target, self.timestamp, self.value)
    
    def __eq__(self, other):
        return self.equality_tuple() == other.equality_tuple()
    
    def __hash__(self):
        return hash(self.equality_tuple())
        
    def __ne__(self, other):
        return not(self == other)
        
    def importantKnowledge(self):
        return self.action in [Actions.KILL, Actions.BEAT_UP, Actions.INSULT, Actions.OWNED_BY]

class Actions(Enum):
  KILL = "killed"
  BEAT_UP = "beat up"
  INSULT = "insulted"
  CONVERSE = "conversed with"
  LOCATED_IN = "located in"
  OWNED_BY = "owned by"
  LIKES = "likes"
  NONE = "none"

  @property
  def is_witnessed(self):
    if self in [Actions.KILL, Actions.BEAT_UP]:
      return True
    else:
      return False
  
  @property
  def ignore_if_self_is_target(self):
    return self in [Actions.KILL, Actions.BEAT_UP, Actions.OWNED_BY]
  
  @property
  def react_badly_if_conflicting_subjects(self):
    return self in [Actions.KILL, Actions.BEAT_UP]
  
  @property
  def react_badly_if_conflicting_targets(self):
    return False

  @property
  def importantEvent(self):
    return self in [Actions.KILL, Actions.BEAT_UP, Actions.INSULT]

class GoalType(Enum):
  GET_OBJECT = 1
  BEFRIEND = 2
  KILL = 3
  NONE = 4

class Goal:
  '''Represents the goals of characters between each other'''
  def __init__(self, type, target1 = None, target2 = None):
    self.type = type # type: GoalType
    self.target1 = target1 # type: Character
    self.target2 = target2 # type: Character
