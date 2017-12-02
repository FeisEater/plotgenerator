import random
from enum import Enum

def persons_house(person):
  return "{}'s house".format(person.name)

def persons_shop(person):
  return "{}'s shop".format(person.name)
  
TAVERN = "tavern"

class Character:
    def __init__(self, name, location = None, output = []):
        self.relationships = {}
        self.name = name
        self.schedule_time = 0
        self.location = location if location is not None else persons_house(self)
        self.knowledge = [] # Knowledge character has acquired through witnessing or conversing with other characters
        self.out = output # Queue output so we can filter out unimportant output later
        
        self.reactions = {
          Actions.KILL: self.react_to_kill,
          Actions.BEAT_UP: self.react_to_beat_up
        }

    def schedule_step(self):
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
        self.out.append("-" + self.name + " found out that " + knowledge.source.name + " " + knowledge.action.value + " " + knowledge.target.name)
        if knowledge.source == self or knowledge.target == self:
          return
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
        self.source = source
        self.action = action
        self.target = target
        self.timestamp = timestamp

class Actions(Enum):
  KILL = "kill"
  BEAT_UP = "beat up"
  INSULT = "insult"
  CONVERSE = "converse"
  NONE = "none"

  @property
  def is_witnessed(self):
    if self in [Actions.KILL, Actions.BEAT_UP]:
      return True
    else:
      return False
