import random
from enum import Enum
from utilities import safe_append, safe_extend, persons_house, persons_shop, TAVERN

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
        assert owner is None or isinstance(owner, Character)

        self.location = location # type: str
        self.owner = owner # type: Character

class Location(Thing):
    def __init__(self, name):
      Thing.__init__(self, name)

class Character(Thing):
    def __init__(self, name, location = None, positive_talking_points = set(), negative_talking_points = set(), political_views = set(), output = []):
        Thing.__init__(self, name)
        self.relationships = {}
        self.schedule_time = 0
        self.location = location if location is not None else Location(persons_house(self))
        self.knowledge = [] # Knowledge character has acquired through witnessing or conversing with other characters
        self.told_knowledge = {} # Knowledge that was already told. Key: other person, Value: knowledge
        self.out = output # Queue output so we can filter out unimportant output later
        self.positive_talking_points = positive_talking_points # type: list
        self.negative_talking_points = negative_talking_points # type: list
        self.goals = [Goal(GoalType.NONE)] # prioritised list of goals
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
          GoalType.NONE: self.do_schedule
        }

    def __str__(self):
        return "Name: {NAME} Goals {GOALS} Political views: {POLITICAL_VIEWS} Location: {LOCATION} Positive talking points: {POSITIVE_TALKING_POINTS} Negative talking points: {NEGATIVE_TALKING_POINTS} Dead: {DEAD}".format(NAME = self.name, GOALS = self.goals, LOCATION = self.location, POLITICAL_VIEWS = self.political_views, POSITIVE_TALKING_POINTS = self.positive_talking_points, NEGATIVE_TALKING_POINTS = self.negative_talking_points, DEAD = self.dead)

    def __repr__(self):
        return "<Character {}>".format(self.__str__())

    def findThing(self, thing):
        wrong_knowledge = False
        for know in self.knowledge:
          if know.action == Actions.LOCATED_IN and know.subject == thing:
            if self.location == know.target:
              if thing.location == self.location:
                return True
              else:
                wrong_knowledge = True
                break
            else:
              self.location = know.target
              self.out.append(self.name + " goes to " + self.location.name)
              return False
          elif know.action == Actions.OWNED_BY and know.subject == thing:
            self.findThing(know.target)
        if wrong_knowledge:
          self.knowledge = [k for k in self.knowledge if not(k.subject == thing and k.action == Actions.LOCATED_IN and k.target == self.location)]
          self.out.append(self.name + " didnt find " + thing.name + " from " + self.location.name)
          return False
        if self.schedule_time <= 0:
          locations = [Location(persons_shop(x)) for x in self.relationships.keys()] + [Location(TAVERN)]
          self.location = random.choice(locations)
          self.out.append(self.name + " goes to " + self.location.name)
          self.schedule_time = random.randint(1, 3)    
    
    def do_getObject(self, arg1, arg2, step):
        if self.findThing(arg1):
          arg1.owner = self
          arg1.location = None
          self.goals = [goal for goal in self.goals if goal.target1 != arg1]
          self.knowledge = [know for know in self.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == arg1)]
          self.knowledge.append(Knowledge(self, arg1, Actions.OWNED_BY, self, step))
          self.out.append(self.name + " got " + arg1.name)

    def do_befriend(self, arg1, arg2, step):
        if arg2 == None:
          print("not implemented")
        else:
          print("not implemented")

    def do_kill(self, arg1, arg2, step):
        if arg2 == None:
          self.findThing(arg1)
        else:
          # self wants arg1 to kill arg2
          if arg1.location != self.location:
            return
          if arg1.relationships[self] < 0:
            # self.do_befriend(arg1)
            return
          knownObjects = [know.subject for know in self.knowledge if (know.action == Actions.LOCATED_IN or know.action == Actions.OWNED_BY) and type(know.subject) is Object]
          acquaintances = [person for person in arg1.relationships.keys() if arg1.relationships[person] >= 0 and arg1.relationships[person] < 0.5]
          friends = [person for person in arg1.relationships.keys() if arg1.relationships[person] >= 0.5]
          if knownObjects and random.random() < 0.5:
            self.tellLie(arg1, random.choice(knownObjects), Actions.OWNED_BY, arg2, step)
          else:
            if friends:
              deadFriends = [friend for friend in friends if friend.dead]
              if deadFriends:
                deadFriend = random.choice(deadFriends)
                self.tellLie(arg1, arg2, Actions.KILL, deadFriend, step)
              else:
                friend = random.choice(friends)
                self.tellLie(arg1, arg2, Actions.BEAT_UP, friend, step)
            elif acquaintances:
              acquaintance = random.choice(acquaintances)
              self.tellLie(arg1, arg2, Actions.BEAT_UP, acquaintance, step)
    
    def do_schedule(self, arg1, arg2, step):
        if self.schedule_time <= 0:
            if self.location.name == persons_house(self):
                self.location = Location(persons_shop(self))
                self.out.append(self.name + " goes to " + self.location.name)
                self.schedule_time = random.randint(2, 8)
            else:
                locations = [Location(persons_shop(x)) for x in self.relationships.keys() if not x.dead] + [Location(TAVERN), Location(persons_house(self))]
                self.location = random.choice(locations)
                self.out.append(self.name + " goes to " + self.location.name)
                if self.location.name == persons_house(self):
                    self.schedule_time = random.randint(2, 8)
                elif self.location.name == TAVERN:
                    self.schedule_time = random.randint(1, 4)

    def tellLie(self, target, arg1, action, arg2, step):
      lie = Knowledge(self, arg1, action, arg2, step)
      safe_append(target.told_knowledge, self, lie)
      safe_append(self.told_knowledge, target, lie)
      target.acquire_knowledge(lie)
      self.out.append("-of course, " + self.name + " was lying to " + target.name)
        
    def schedule_step(self, step):
        #self.knowledge = [know for know in self.knowledge if not(know.subject == self and know.action == Actions.LIKES)]
        #self.knowledge = [Knowledge(self, self, Actions.LIKES, x, step, self.relationships[x]) for x in self.relationships.keys()]
        goal = self.goals[0]
        self.schedule_methods[goal.type](goal.target1, goal.target1, step)
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

    def source_trust(self, source):
      if self == source:
        return 1
      return self.relationships[source]

    def choose_who_to_trust(self, newsource, oldsources):
      oldsources.sort(key=lambda source: self.source_trust(source), reverse=True)
      if self.relationships[oldsources[0]] < self.relationships[newsource] or newsource == self:
        for source in oldsources:
          self.change_relationship(source, -0.25)
          self.knowledge = [know for know in self.knowledge if not(know.source == source)]
          return True
      if self.relationships[oldsources[0]] > self.relationships[newsource] or oldsources[0] == self:
        self.change_relationship(newsource, -0.25)
        return False
      if random.random() < 0.5:
        for source in oldsources:
          self.change_relationship(source, -0.25)
          self.knowledge = [know for know in self.knowledge if not(know.source == source)]
          return True
      self.change_relationship(newsource, -0.25)
      return False
    
    def acquire_knowledge(self, knowledge):
        if knowledge in self.knowledge:
          return
        if knowledge.subject == self and knowledge.source != self:
          return
        if knowledge.target == self and knowledge.source != self and knowledge.action.ignore_if_self_is_target:
          return
        conflicting_sources = [know.source for know in self.knowledge if know.subject == knowledge.subject and know.target != knowledge.target]
        if conflicting_sources and knowledge.action.react_badly_if_conflicting_targets:
          if self.choose_who_to_trust(knowledge.source, conflicting_sources):
            self.knowledge.append(knowledge)
            self.out.append("-" + self.name + " found out from " + knowledge.source.name + " that " + knowledge.subject.name + " " + knowledge.action.value + " " + knowledge.target.name + " " + str(knowledge.value))
            if knowledge.action in self.reactions.keys():
              self.reactions[knowledge.action](knowledge)
            for source in oldsources:
              self.out.append("-That meant that " + str(conflicting_sources) + " were lying")
          else:
            self.out.append("-" + self.name + " found out from " + knowledge.source.name + " that " + knowledge.subject.name + " " + knowledge.action.value + " " + knowledge.target.name + " " + str(knowledge.value))
            self.out.append("-But " + self.name + " would not believe it!")
        else:
          self.knowledge.append(knowledge)
          self.out.append("-" + self.name + " found out from " + knowledge.source.name + " that " + knowledge.subject.name + " " + knowledge.action.value + " " + knowledge.target.name + " " + str(knowledge.value))
          if knowledge.action in self.reactions.keys():
            self.reactions[knowledge.action](knowledge)
    
    def react_to_kill(self, knowledge):
        if self == knowledge.target:
          return
        self.goals = [goal for goal in self.goals if not(goal.type == GoalType.KILL and (goal.target1 == knowledge.target or goal.target2 == knowledge.target))]
        if self.relationships[knowledge.target] > 0.5:
          self.relationships[knowledge.subject] = -1
          self.goals.insert(0, Goal(GoalType.KILL, knowledge.subject))
          self.out.append("-" + self.name + " vowes revenge on " + knowledge.subject.name)
        elif self.relationships[knowledge.target] > 0:
          self.change_relationship(knowledge.subject, -0.25)
        elif self.relationships[knowledge.target] < -0.5:
          self.change_relationship(knowledge.subject, 0.25)

    def react_to_beat_up(self, knowledge):
        if self == knowledge.target:
          return
        if self.relationships[knowledge.target] > 0.5:
          self.change_relationship(knowledge.subject, -0.5)
        elif self.relationships[knowledge.target] > 0:
          self.change_relationship(knowledge.subject, -0.25)
        if self.relationships[knowledge.target] < -0.5:
          self.change_relationship(knowledge.subject, 0.25)

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
