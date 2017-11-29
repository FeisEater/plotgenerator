import random

class Character:
    def __init__(self, name, location = None, opponent = None, output = []):
        self.relationships = {} #{ opponent: -1 } if isinstance(opponent, str) else {}
        self.name = name
        self.schedule_time = 0
        self.location = location if location is not None else self.name + "'s house"
        self.knowledge = [] # Knowledge character has acquired through witnessing or conversing with other characters
        self.out = output # Queue output so we can filter out unimportant output later

    def schedule_step(self):
        if self.schedule_time <= 0:
            if self.location == self.name + "'s house":
                self.location = self.name + "'s shop"
                self.out.append(self.name + " goes to " + self.location)
                self.schedule_time = random.randint(2, 8)
            else:
                locations = ["{}'s shop".format(x.name) for x in self.relationships.keys()] + ["tavern", "{}'s house".format(self.name)]
                self.location = random.choice(locations)
                self.out.append(self.name + " goes to " + self.location)
                if self.location == self.name + "'s house":
                    self.schedule_time = random.randint(2, 8)
                elif self.location == "tavern":
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
        self.out.append("-" + self.name + " found out that " + knowledge.source.name + " " + knowledge.relation + " " + knowledge.target.name)
        if knowledge.source == self or knowledge.target == self:
          return
        if knowledge.relation == "killed":
          if self.relationships[knowledge.target] > 0.5:
            self.relationships[knowledge.source] = -1
            self.out.append("-" + self.name + " vowes revenge on " + knowledge.source.name)
          elif self.relationships[knowledge.target] > 0:
            self.change_relationship(knowledge.source, -0.25)
          if self.relationships[knowledge.target] < -0.5:
            self.change_relationship(knowledge.source, 0.25)
        elif knowledge.relation == "beat up":
          if self.relationships[knowledge.target] > 0.5:
            self.change_relationship(knowledge.source, -0.5)
          elif self.relationships[knowledge.target] > 0:
            self.change_relationship(knowledge.source, -0.25)
          if self.relationships[knowledge.target] < -0.5:
            self.change_relationship(knowledge.source, 0.25)

class Knowledge:
    def __init__(self, source, relation, target, timestamp):
        self.source = source
        self.relation = relation
        self.target = target
        self.timestamp = timestamp