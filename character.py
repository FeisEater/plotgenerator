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
        self.protagonist = False

        self.reactions = {
          Actions.KILL: self.react_to_kill,
          Actions.BEAT_UP: self.react_to_beat_up
        }

        self.schedule_methods = {
          GoalType.GET_OBJECT: self.sched_getObject,
          GoalType.BEFRIEND: self.sched_befriend,
          GoalType.KILL: self.sched_kill,
          GoalType.NONE: self.sched_none
        }
        
        self.action_methods = {
          Actions.KILL: self.do_kill,
          Actions.BEAT_UP: self.do_beat_up,
          Actions.INSULT: self.do_insult,
          Actions.CONVERSE: self.do_converse
        }
    
    def setWorldData(self, locations, objects):
        self.locations = locations
        self.objects = objects

    def __str__(self):
        return "Name: {NAME} Goals {GOALS} Political views: {POLITICAL_VIEWS} Location: {LOCATION} Domains: {DOMAINS} Positive talking points: {POSITIVE_TALKING_POINTS} Negative talking points: {NEGATIVE_TALKING_POINTS} Dead: {DEAD}".format(NAME = self.name, GOALS = self.goals, LOCATION = self.location, POLITICAL_VIEWS = self.political_views, DOMAINS = self.domains, POSITIVE_TALKING_POINTS = self.positive_talking_points, NEGATIVE_TALKING_POINTS = self.negative_talking_points, DEAD = self.dead)

    def __repr__(self):
        return "<Character {}>".format(self.__str__())

    def findThing(self, thing):
        wrong_knowledge = False
        tried_locations = [know.target for know in self.knowledge if know.action == Actions.NOT_LOCATED_IN]
        for know in self.knowledge:
          if know.action == Actions.LOCATED_IN and know.subject == thing and know.target not in tried_locations:
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
          self.knowledge.append(Knowledge(self, thing, Actions.NOT_LOCATED_IN, self.location, self.step))
          context = [output.Context(output.GoesTo, {'character': self, 'place': self.location})]
          self.out.append(output.DidntFind(self.step, self.location, context, self, thing))
          return False
        self.sched_none(None, None)
    
    def sched_getObject(self, arg1, arg2):
        if self.findThing(arg1):
          arg1.owner = self
          arg1.location = None
          self.goals = [goal for goal in self.goals if goal.target1 != arg1]
          self.knowledge = [know for know in self.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == arg1)]
          self.knowledge.append(Knowledge(self, arg1, Actions.OWNED_BY, self, self.step))
          context = [output.Context(output.GoesTo, {'character': self, 'place': self.location})]
          self.out.append(output.Got(self.step, self.location, context, self, arg1))

    def sched_befriend(self, arg1, arg2):
        if arg2 == None:
          print("not implemented")
        else:
          print("not implemented")

    def sched_kill(self, arg1, arg2):
        if arg2 == None:
          self.findThing(arg1)
        else:
          # self wants arg1 to kill arg2
          if arg1.location != self.location:
            self.sched_none(None, None)
            return
          if arg1.relationships[self] < 0:
            method_tuple = self.do_converse(arg1, [])
            converseOutput = [output.SomeAction(self.step, self.location, [], self, arg1, Actions.CONVERSE)] + method_tuple[1]
            self.out.extend(converseOutput)
            return
          knownObjects = [know for know in self.knowledge if (know.action == Actions.LOCATED_IN or know.action == Actions.OWNED_BY) and type(know.subject) is Object]
          acquaintances = [know for know in self.knowledge if know.subject == arg1 and know.action == Actions.LIKES and know.value >= 0 and know.value < 0.5]
          friends = [know for know in self.knowledge if know.subject == arg1 and know.action == Actions.LIKES and know.value >= 0.5]
          if knownObjects and random.random() < 0.5:
            targetObjectKnowledge = random.choice(knownObjects)
            self.tellLie(arg1, targetObjectKnowledge.subject, Actions.OWNED_BY, arg2, targetObjectKnowledge)
            safe_extend(self.told_knowledge, arg1, [know for know in self.knowledge if know.subject == targetObjectKnowledge.subject])
          else:
            if friends:
              deadFriends = [friend for friend in friends if friend.target.dead]
              if deadFriends:
                deadFriendKnowledge = random.choice(deadFriends)
                self.tellLie(arg1, arg2, Actions.KILL, deadFriendKnowledge.target, deadFriendKnowledge)
                safe_extend(self.told_knowledge, arg1, [know for know in self.knowledge if know.target == deadFriendKnowledge.target and know.action == Actions.KILL])
              else:
                friendKnowledge = random.choice(friends)
                self.tellLie(arg1, arg2, Actions.BEAT_UP, friendKnowledge.target, friendKnowledge)
                safe_extend(self.told_knowledge, arg1, [know for know in self.knowledge if know.target == friendKnowledge.target and know.action == Actions.BEAT_UP])
            elif acquaintances:
              acquaintanceKnowledge = random.choice(acquaintances)
              self.tellLie(arg1, arg2, Actions.BEAT_UP, acquaintanceKnowledge.target, acquaintanceKnowledge)
              safe_extend(self.told_knowledge, arg1, [know for know in self.knowledge if know.target == acquaintanceKnowledge.target and know.action == Actions.BEAT_UP])
    
    def sched_none(self, arg1, arg2):
        if self.schedule_time <= 0:
            newlocation = random.choice([loc for loc in self.locations if self.location != loc])
            self.out.append(output.GoesTo(self.step, self.location, [], self, newlocation))
            self.location = newlocation
            self.schedule_time = random.randint(2, 8)
            '''if self.location.name == persons_house(self):
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
                    self.schedule_time = random.randint(1, 4)'''

    def tellLie(self, target, arg1, action, arg2, contextKnowledge):
      lie = Knowledge(self, arg1, action, arg2, self.step)
      safe_append(target.told_knowledge, self, lie)
      safe_append(self.told_knowledge, target, lie)
      target.acquire_knowledge(lie)
      context = [
        output.Context(output.ExposManipulationMotivation, {'subject': self, 'killer': target}),
        output.Context(output.KnowledgeLearned, {'learner': self, 'knowledge': contextKnowledge}),
        output.Context(output.KnowledgeLearned, {'learner': target, 'knowledge': lie})
      ]
      self.out.append(output.WasLying(self.step, self.location, context, self, target, lie))
        
    def schedule_step(self, step):
        self.knowledge = [know for know in self.knowledge if not(know.subject == self and know.action == Actions.LIKES)]
        self.knowledge.extend([Knowledge(self, self, Actions.LIKES, x, step, self.relationships[x]) for x in self.relationships.keys()])
        self.step = step
        goal = self.goals[0]
        self.schedule_methods[goal.type](goal.target1, goal.target2)
        self.schedule_time -= 1
    
    def change_relationship(self, person, delta, context, printNow=True):
        if self == person or person not in self.relationships:
          return
        oldvalue = self.relationships[person]
        self.relationships[person] += delta
        if self.relationships[person] > 1:
          self.relationships[person] = 1
        if self.relationships[person] < -1:
          self.relationships[person] = -1
        pendingOutput = output.RelationshipChange(self.step, self.location, context, self, person, oldvalue, self.relationships[person])
        if printNow:
          self.out.append(pendingOutput)
        else:
          return pendingOutput

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
              self.knowledge = [know for know in self.knowledge if not(know.source == source)]
              context = [output.Context(output.KnowledgeLearned, {'learner': self, 'knowledge.source': source})]
              self.out.append(output.LieReveal(self.step, self.location, context, self, source))
              self.change_relationship(source, -0.25, [])
          else:
            self.out.append(output.KnowledgeLearned(self.step, self.location, discussionContext, self, knowledge))
            context = [output.Context(output.KnowledgeLearned, {'learner': self, 'knowledge': knowledge})]
            self.out.append(output.NewInfoIsLie(self.step, self.location, context, self, knowledge))
            self.change_relationship(knowledge.source, -0.25, [])
        else:
          self.knowledge.append(knowledge)
          if not(knowledge.source == self and (knowledge.subject == self or knowledge.target == self)):
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

    def do_kill(source, target, chars_to_ignore):
      target.dead = True
      chars_to_ignore.append(target)
      source.knowledge = [know for know in source.knowledge if not(know.action == Actions.OWNED_BY and know.target == target)]
      additionalOutput = []
      for object in source.objects:
        if object.owner == target:
          source.knowledge = [know for know in source.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == object)]
          object.owner = source
          object.location = None
          source.goals = [goal for goal in source.goals if goal.target1 != object]
          context = [output.Context(output.Got, {'character': target, 'object': object})]
          additionalOutput.append(output.Steal(source.step, source.location, context, source, target, object))
      source.schedule_time = 0
      return ([
        output.Context(output.ExposRelationship, {'source': source, 'target': target}),
        output.Context(output.ExposRelationship, {'source': target, 'target': source}),
        output.Context(output.RelationshipChange, {'source': source, 'target': target}),
        output.Context(output.VowRevenge, {'source': source, 'target': target}),
      ], additionalOutput)

    def do_beat_up(source, target, chars_to_ignore):
      pendingOutput = target.change_relationship(source, -1, [], False)
      chars_to_ignore.append(target)
      source.knowledge = [know for know in source.knowledge if not(know.action == Actions.OWNED_BY and know.target == target)]
      additionalOutput = [pendingOutput]
      for object in source.objects:
        if object.owner == target:
          source.knowledge = [know for know in source.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == object)]
          object.owner = source
          object.location = None
          source.goals = [goal for goal in source.goals if goal.target1 != object]
          context = [output.Context(output.Got, {'character': target, 'object': object})]
          additionalOutput.append(output.Steal(source.step, source.location, context, source, target, object))
      source.schedule_time = 0
      return ([
        output.Context(output.ExposRelationship, {'source': source, 'target': target}),
        output.Context(output.ExposRelationship, {'source': target, 'target': source}),
        output.Context(output.RelationshipChange, {'source': source, 'target': target}),
      ], additionalOutput)

    def do_insult(source, target, chars_to_ignore):
      pendingOutput = target.change_relationship(source, -0.25, [], False)
      return ([
        output.Context(output.ExposRelationship, {'source': source, 'target': target}),
        output.Context(output.ExposRelationship, {'source': target, 'target': source}),
        output.Context(output.RelationshipChange, {'source': source, 'target': target}),
      ], [pendingOutput])

    def do_converse(source, target, chars_to_ignore):
      pendingOutput = target.change_relationship(source, 0.25, [], False)
      if source in target.told_knowledge:
        untold_knowledge = [x for x in target.knowledge if x not in target.told_knowledge[source]]
      else:
        untold_knowledge = [x for x in target.knowledge]
      relationshipGossip = [x for x in untold_knowledge if x.action == Actions.LIKES]
      eventGossip = [x for x in untold_knowledge if x.action != Actions.LIKES]
      topics_rel = relationshipGossip if len(relationshipGossip) <= 3 else random.sample(relationshipGossip, 3)
      topics_eve = eventGossip if len(eventGossip) <= 3 else random.sample(eventGossip, 3)
      conversation_topics = topics_eve + topics_rel
      for topic in conversation_topics:
        topic.source = target
        safe_append(target.told_knowledge, source, topic)
        safe_append(source.told_knowledge, target, topic)
        source.acquire_knowledge(topic)
      return ([
        output.Context(output.ExposRelationship, {'source': source, 'target': target}),
        output.Context(output.ExposRelationship, {'source': target, 'target': source}),
        output.Context(output.RelationshipChange, {'source': source, 'target': target}),
      ], [pendingOutput])
    
    def make_decision(source, target):
      if [goal for goal in source.goals if goal.type == GoalType.KILL and goal.target1 == target and goal.target2 == None]:
        return Actions.KILL
      if [goal.target1 for goal in source.goals if goal.type == GoalType.GET_OBJECT and goal.target1.owner == target]:
        if source.relationships[target] < -0.75:
          return Actions.KILL
        else:
          return Actions.BEAT_UP
      if source.relationships[target] < -0.75:
        return Actions.KILL
      if source.relationships[target] < -0.5:
        return Actions.BEAT_UP
      if source.relationships[target] < -0.25:
        return Actions.INSULT
      if source.relationships[target] > 0:
        return Actions.CONVERSE
      return Actions.NONE

    def description(self):
        "{NAME}".format(NAME=self.name)