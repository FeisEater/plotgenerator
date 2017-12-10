import random
from models import Thing, Object, Knowledge, Location, Goal, GoalType, Actions
from utilities import safe_append, safe_extend, persons_house, persons_shop, TAVERN
import output

class Character(Thing):
    def __init__(self, name, location = None, positive_talking_points = set(), negative_talking_points = set(), political_views = set(), domains = set(), out = []):
        Thing.__init__(self, name)
        self.relationships = {}
        self.schedule_time = 0
        self.location = location if location is not None else Location(persons_house(self))
        self.knowledge = [] # Knowledge character has acquired through witnessing or conversing with other characters
        self.told_knowledge = {} # Knowledge that was already told. Key: other person, Value: knowledge
        self.out = out # Queue output so we can filter out unimportant output later
        self.positive_talking_points = positive_talking_points # type: list
        self.negative_talking_points = negative_talking_points # type: list
        self.goals = [Goal(GoalType.NONE)] # prioritised list of goals
        self.political_views = political_views # type: set
        self.domains = domains # type: set
        self.dead = False
        self.step = 0

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
        return "Name: {NAME} Goals {GOALS} Political views: {POLITICAL_VIEWS} Location: {LOCATION} Domains: {DOMAINS} Positive talking points: {POSITIVE_TALKING_POINTS} Negative talking points: {NEGATIVE_TALKING_POINTS} Dead: {DEAD}".format(NAME = self.name, GOALS = self.goals, LOCATION = self.location, POLITICAL_VIEWS = self.political_views, DOMAINS = self.domains, POSITIVE_TALKING_POINTS = self.positive_talking_points, NEGATIVE_TALKING_POINTS = self.negative_talking_points, DEAD = self.dead)

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
              context = [output.Context(output.KnowledgeLearned, {'learner': self, 'knowledge': know})]
              self.out.append(output.GoesTo(self.step, self.location, context, self, know.target, True))
              self.location = know.target
              return False
          elif know.action == Actions.OWNED_BY and know.subject == thing:
            self.findThing(know.target)
        if wrong_knowledge:
          self.knowledge = [k for k in self.knowledge if not(k.subject == thing and k.action == Actions.LOCATED_IN and k.target == self.location)]
          context = [output.Context(output.GoesTo, {'character': self, 'place': self.location})]
          self.out.append(output.DidntFind(self.step, self.location, context, self, thing))
          return False
        if self.schedule_time <= 0:
          locations = [Location(persons_shop(x)) for x in self.relationships.keys()] + [Location(TAVERN)]
          newlocation = random.choice(locations)
          self.out.append(output.GoesTo(self.step, self.location, [], self, newlocation))
          self.location = newlocation
          self.schedule_time = random.randint(1, 3)    
    
    def do_getObject(self, arg1, arg2):
        if self.findThing(arg1):
          arg1.owner = self
          arg1.location = None
          self.goals = [goal for goal in self.goals if goal.target1 != arg1]
          self.knowledge = [know for know in self.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == arg1)]
          self.knowledge.append(Knowledge(self, arg1, Actions.OWNED_BY, self, self.step))
          context = [output.Context(output.GoesTo, {'character': self, 'place': self.location})]
          self.out.append(output.Got(self.step, self.location, context, self, arg1))

    def do_befriend(self, arg1, arg2):
        if arg2 == None:
          print("not implemented")
        else:
          print("not implemented")

    def do_kill(self, arg1, arg2):
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
            self.tellLie(arg1, random.choice(knownObjects), Actions.OWNED_BY, arg2)
          else:
            if friends:
              deadFriends = [friend for friend in friends if friend.dead]
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
            if self.location.name == persons_house(self):
                newlocation = Location(persons_shop(self))
                self.out.append(output.GoesTo(self.step, self.location, [], self, newlocation))
                self.location = newlocation
                self.schedule_time = random.randint(2, 8)
            else:
                locations = [Location(persons_shop(x)) for x in self.relationships.keys() if not x.dead] + [Location(TAVERN), Location(persons_house(self))]
                newlocation = random.choice(locations)
                self.out.append(output.GoesTo(self.step, self.location, [], self, newlocation))
                self.location = newlocation
                if self.location.name == persons_house(self):
                    self.schedule_time = random.randint(2, 8)
                elif self.location.name == TAVERN:
                    self.schedule_time = random.randint(1, 4)

    def tellLie(self, target, arg1, action, arg2):
      lie = Knowledge(self, arg1, action, arg2, self.step)
      safe_append(target.told_knowledge, self, lie)
      safe_append(self.told_knowledge, target, lie)
      target.acquire_knowledge(lie)
      context = [output.Context(output.ExposManipulationMotivation, {'subject': self, 'killer': target})]
      self.out.append(output.WasLying(self.step, self.location, context, self, target, lie))
        
    def schedule_step(self, step):
        #self.knowledge = [know for know in self.knowledge if not(know.subject == self and know.action == Actions.LIKES)]
        #self.knowledge = [Knowledge(self, self, Actions.LIKES, x, step, self.relationships[x]) for x in self.relationships.keys()]
        self.step = step
        goal = self.goals[0]
        self.schedule_methods[goal.type](goal.target1, goal.target1)
        self.schedule_time -= 1
    
    def change_relationship(self, person, delta, context):
        if self == person or person not in self.relationships:
          return
        oldvalue = self.relationships[person]
        self.relationships[person] += delta
        if self.relationships[person] > 1:
          self.relationships[person] = 1
        if self.relationships[person] < -1:
          self.relationships[person] = -1
        self.out.append(output.RelationshipChange(self.step, self.location, context, self, person, oldvalue, self.relationships[person]))

    def source_trust(self, source):
      if self == source:
        return 1
      return self.relationships[source]

    def choose_who_to_trust(self, newsource, oldsources):
      oldsources.sort(key=lambda source: self.source_trust(source), reverse=True)
      if self.relationships[oldsources[0]] < self.relationships[newsource] or newsource == self:
        for source in oldsources:
          return True
      if self.relationships[oldsources[0]] > self.relationships[newsource] or oldsources[0] == self:
        return False
      if random.random() < 0.5:
        for source in oldsources:
          return True
      return False
    
    def acquire_knowledge(self, knowledge):
        if knowledge in self.knowledge:
          return
        if knowledge.subject == self and knowledge.source != self:
          return
        if knowledge.target == self and knowledge.source != self and knowledge.action.ignore_if_self_is_target:
          return
        discussionContext = [output.Context(output.SomeAction, {'source': self, 'target': knowledge.source, 'action': Actions.CONVERSE})]
        conflicting_sources = [know.source for know in self.knowledge if know.subject == knowledge.subject and know.target != knowledge.target]
        if conflicting_sources and knowledge.action.react_badly_if_conflicting_targets:
          if self.choose_who_to_trust(knowledge.source, conflicting_sources):
            self.knowledge.append(knowledge)
            self.out.append(output.KnowledgeLearned(self.step, self.location, discussionContext, self, knowledge))
            if knowledge.action in self.reactions.keys():
              self.reactions[knowledge.action](knowledge)
            for source in conflicting_sources:
              self.change_relationship(source, -0.25, [])
              self.knowledge = [know for know in self.knowledge if not(know.source == source)]
              context = [output.Context(output.KnowledgeLearned, {'learner': self, 'knowledge.source': source})]
              self.out.append(output.LieReveal(self.step, self.location, context, self, source))
          else:
            self.change_relationship(knowledge.source, -0.25, [])
            self.out.append(output.KnowledgeLearned(self.step, self.location, discussionContext, self, knowledge))
            context = [output.Context(output.KnowledgeLearned, {'learner': self, 'knowledge': knowledge})]
            self.out.append(output.NewInfoIsLie(self.step, self.location, context, self, knowledge))
        else:
          self.knowledge.append(knowledge)
          self.out.append(output.KnowledgeLearned(self.step, self.location, discussionContext, self, knowledge))
          if knowledge.action in self.reactions.keys():
            self.reactions[knowledge.action](knowledge)
    
    def react_to_kill(self, knowledge):
        if self == knowledge.target:
          return
        context = [
          output.Context(output.ExposRelationship, {'source': self, 'target': knowledge.target}),
          output.Context(output.ExposRelationship, {'source': knowledge.target, 'target': self}),
          output.Context(output.RelationshipChange, {'source': self, 'target': knowledge.target}),
        ]
        self.goals = [goal for goal in self.goals if not(goal.type == GoalType.KILL and (goal.target1 == knowledge.target or goal.target2 == knowledge.target))]
        if self.relationships[knowledge.target] > 0.5:
          self.relationships[knowledge.subject] = -1
          self.goals.insert(0, Goal(GoalType.KILL, knowledge.subject))
          context = [output.Context(output.KnowledgeLearned, {'learner': self, 'knowledge': knowledge})]
          self.out.append(output.VowRevenge(self.step, self.location, context, self, knowledge.subject, knowledge.target))
        elif self.relationships[knowledge.target] > 0:
          self.change_relationship(knowledge.subject, -0.25, context)
        elif self.relationships[knowledge.target] < -0.5:
          self.change_relationship(knowledge.subject, 0.25, context)

    def react_to_beat_up(self, knowledge):
        if self == knowledge.target:
          return
        context = [
          output.Context(output.ExposRelationship, {'source': self, 'target': knowledge.target}),
          output.Context(output.ExposRelationship, {'source': knowledge.target, 'target': self}),
          output.Context(output.RelationshipChange, {'source': self, 'target': knowledge.target}),
        ]
        if self.relationships[knowledge.target] > 0.5:
          self.change_relationship(knowledge.subject, -0.5, context)
        elif self.relationships[knowledge.target] > 0:
          self.change_relationship(knowledge.subject, -0.25, context)
        elif self.relationships[knowledge.target] < -0.5:
          self.change_relationship(knowledge.subject, 0.25, context)
