import random
from enum import Enum

def persons_house(person):
  return "{}'s house".format(person.name)

def persons_shop(person):
  return "{}'s shop".format(person.name)
  
TAVERN = "tavern"

class Thing:
    '''A base class for all objects in the simulation.'''
    def __init__(self, name):
        '''
        :param name: The name of the thing.
        :type name: str
        '''
        self.name = name # type: str
    
    def __eq__(self, other):
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)
        
    def __ne__(self, other):
        return not(self == other)
        
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
        super().__init__(self, name)
        assert isinstance(owner, Character)

        self.location = location # type: str
        self.owner = owner # type: Character

class Character(Thing):
    def findThing(self, thing):
        wrong_knowledge = False
        for know in self.knowledge:
          if know.action == Actions.LOCATED_IN and know.source == thing:
            if self.location == know.target:
              if thing.location == self.location:
                return True
              else:
                wrong_knowledge = True
                break
            else:
              self.location = know.target
              self.out.append(self.name + " goes to " + self.location)
              return False
        if wrong_knowledge:
          self.knowledge = [k for k in self.knowledge if k.source != thing or k.action != Actions.LOCATED_IN or k.target != self.location]
          self.out.append(self.name + " didnt find " + thing.name + " from " + self.location)
          return False
        if self.schedule_time <= 0:
          locations = [persons_shop(x) for x in self.relationships.keys()] + [TAVERN]
          self.location = random.choice(locations)
          self.out.append(self.name + " goes to " + self.location)
          self.schedule_time = random.randint(1, 3)    
    
    def do_getObject(self, arg1, arg2):
        if self.findThing(arg1):
          arg1.owner = self
          self.goal.pop(0)
          self.out.append(self.name + " got " + arg1.name)

    def do_befriend(self, arg1, arg2):
        if arg2 == None:
          print("not implemented")
        else:
          print("not implemented")

    def do_kill(self, arg1, arg2):
        if arg2 == None:
          if self.findThing(arg1):
            arg1.dead = True
            self.out.append(self.name + " killed " + arg1.name)
        else:
          # self wants arg1 to kill arg2
          if arg1.relationships[self] < 0:
            # self.do_befriend(arg1)
            return
          acquaintances = [person for person in arg1.relationships.keys() if arg1.relationships[person] >= 0 and arg1.relationships[person] < 0.5]
          friends = [person for person in arg1.relationships.keys() if arg1.relationships[person] >= 0.5]
          if friends:
            deadFriends = [friend for friend in friends if friends.dead]
            if deadFriends:
              deadFriend = random.choice(deadFriends)
              self.tellLie(arg1, arg2, Actions.KILL, deadFriend)
            else:
              friend = random.choice(friends)
              self.tellLie(arg1, arg2, Actions.BEAT_UP, friend)
          elif acquaintances:
            acquaintance = random.choice(acquaintances)
            self.tellLie(arg1, arg2, Actions.BEAT_UP, acquaintance)
    
    def do_schedule(self, arg1, arg2):
        if self.schedule_time <= 0:
            if self.location == persons_house(self):
                self.location = persons_shop(self)
                self.out.append(self.name + " goes to " + self.location)
                self.schedule_time = random.randint(2, 8)
            else:
                locations = [persons_shop(x) for x in self.relationships.keys()] + [TAVERN, persons_house(self)]
                self.location = random.choice(locations)
                self.out.append(self.name + " goes to " + self.location)
                if self.location == persons_house(self):
                    self.schedule_time = random.randint(2, 8)
                elif self.location == TAVERN:
                    self.schedule_time = random.randint(1, 4)

    def tellLie(self, target, arg1, action, arg2):
      lie = Knowledge(arg1, action, arg2, -1) #TODO: change -1 to step from proto.py later
      #safe_extend(target.told_knowledge, self, lie)
      #safe_extend(self.told_knowledge, target, lie)
      target.acquire_knowledge(lie)
    
    def __init__(self, name, location = None, positive_talking_points = set(), negative_talking_points = set(), political_views = set(), output = []):
        Thing.__init__(self, name)
        self.relationships = {}
        self.schedule_time = 0
        self.location = location if location is not None else persons_house(self)
        self.knowledge = [] # Knowledge character has acquired through witnessing or conversing with other characters
        self.told_knowledge = {} # Knowledge that was already told. Key: other person, Value: knowledge
        self.out = output # Queue output so we can filter out unimportant output later
        self.positive_talking_points = positive_talking_points # type: list
        self.negative_talking_points = negative_talking_points # type: list
        self.goals = [Goal(GoalType.SCHEDULE)] # prioritised list of goals
        self.political_views = political_views # type: set
        self.dead = False

        self.reactions = {
          Actions.KILL: self.react_to_kill,
          Actions.BEAT_UP: self.react_to_beat_up
        }

        self.schedule_methods = {
          GoalType.GET_OBJECT: self.do_getObject,
          GoalType.BEFRIEND: self.do_befriend,
          GoalType.KILL: self.do_kill,
          GoalType.SCHEDULE: self.do_schedule
        }
        
    def schedule_step(self):
        goal = self.goals[0]
        self.schedule_methods[goal.type](goal.target1, goal.target1)
        self.schedule_time -= 1
    
    def change_relationship(self, person, delta):
        if self == person or person not in self.relationships:
          return
        self.relationships[person] += delta
        if self.relationships[person] > 1:
          self.relationships[person] = 1
        if self.relationships[person] < -1:
          self.relationships[person] = -1
        self.out.append("-" + self.name + " likes " + person.name + ": " + str(self.relationships[person]))

    def acquire_knowledge(self, knowledge):
        if knowledge in self.knowledge:
          return
        self.knowledge.append(knowledge)
        if knowledge.source == self or knowledge.target == self:
          return
        self.out.append("-" + self.name + " found out that " + knowledge.source.name + " " + knowledge.action.value + " " + knowledge.target.name)
        self.reactions[knowledge.action](knowledge)
    
    def react_to_kill(self, knowledge):
        if self.relationships[knowledge.target] > 0.5:
          self.relationships[knowledge.source] = -1
          self.out.append("-" + self.name + " vowes revenge on " + knowledge.source.name)
        elif self.relationships[knowledge.target] > 0:
          self.change_relationship(knowledge.source, -0.25)
        elif self.relationships[knowledge.target] < -0.5:
          self.change_relationship(knowledge.source, 0.25)

    def react_to_beat_up(self, knowledge):
        if self.relationships[knowledge.target] > 0.5:
          self.change_relationship(knowledge.source, -0.5)
        elif self.relationships[knowledge.target] > 0:
          self.change_relationship(knowledge.source, -0.25)
        if self.relationships[knowledge.target] < -0.5:
          self.change_relationship(knowledge.source, 0.25)

class Knowledge:
    def __init__(self, source, action, target, timestamp):
        self.source = source # type: Character
        self.action = action # type: Actions
        self.target = target # type: Character
        self.timestamp = timestamp # type: int
        
    def equality_tuple(self):
        return (self.source, self.action, self.target, self.timestamp)
    
    def __eq__(self, other):
        return self.equality_tuple() == other.equality_tuple()
    
    def __hash__(self):
        return hash(self.equality_tuple())
        
    def __ne__(self, other):
        return not(self == other)

class Actions(Enum):
  KILL = "killed"
  BEAT_UP = "beat up"
  INSULT = "insulted"
  CONVERSE = "conversed with"
  LOCATED_IN = "located in"
  LIKES = "likes"
  NONE = "none"

  @property
  def is_witnessed(self):
    if self in [Actions.KILL, Actions.BEAT_UP]:
      return True
    else:
      return False

class GoalType(Enum):
  GET_OBJECT = 1
  BEFRIEND = 2
  KILL = 3
  SCHEDULE = 4

class Goal:
  '''Represents the goals of characters between each other'''
  def __init__(self, type, target1 = None, target2 = None):
    self.type = type # type: GoalType
    self.target1 = target1 # type: Character
    self.target2 = target2 # type: Character
