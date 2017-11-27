import random

class Character:
  def __init__(self):
    self.relationships = {}
    self.name = ""
    self.schedule_time = 0
    self.location = ""
  
  def schedule_step(self):
    if self.schedule_time <= 0:
      if self.location == self.name + "s house":
        self.location = self.name + "s shop"
        print(self.name + " goes to " + self.location)
        self.schedule_time = random.randint(2,8)
      else:
        locations = [x.name + "s shop" for x in self.relationships.keys()] + ["tavern", self.name + "s house"]
        self.location = random.choice(locations)
        print(self.name + " goes to " + self.location)
        if self.location == self.name + "s house":
          self.schedule_time = random.randint(2,8)
        elif self.location == "tavern":
          self.schedule_time = random.randint(1,4)
    self.schedule_time -= 1
        
def safe_append(dict, key, value):
  if key not in dict:
    dict[key] = [value]
  else:
    dict[key].append(value)
    
def change_relationship(person1, person2, delta):
  if person1 == person2 or person2 not in person1.relationships:
    return
  person1.relationships[person2] += delta
  if person1.relationships[person2] > 1:
    person1.relationships[person2] = 1
  if person1.relationships[person2] < -1:
    person1.relationships[person2] = -1
  print("-" + person1.name + " likes " + person2.name + ": " + str(person1.relationships[person2]))

if __name__ == '__main__':
  characters = []
  names = ['John', 'Marsha', 'Patrick', 'Emily', 'George', 'Sarah', 'Ibrahim', 'Natasha', 'Bob', 'Kylie']
  for name in names:
    person = Character()
    person.name = name
    person.location = name + "s house"
    characters.append(person)
  for person in characters:
    for person2 in characters:
      if person == person2:
        continue
      person.relationships[person2] = random.uniform(-1,1)
      print(person.name + " likes " + person2.name + ": " + str(person.relationships[person2]))
  
  while True:
    input("Press Enter to progress...")
    places = {}
    for person in characters:
      person.schedule_step()
      safe_append(places, person.location, person)
    for place in places:
      events = {'kill': [], 'beat up': [], 'insult': [], 'converse': []}
      for person1 in places[place]:
        for person2 in places[place]:
          if person1 == person2:
            continue
          if person1.relationships[person2] < -0.75:
            events['kill'].append((person1, person2))
          elif person1.relationships[person2] < -0.5:
            events['beat up'].append((person1, person2))
          elif person1.relationships[person2] < -0.25:
            events['insult'].append((person1, person2))
          elif person1.relationships[person2] > 0:
            events['converse'].append((person1, person2))
      if not events['kill'] and not events['beat up'] and not events['insult'] and not events['converse']:
        continue
      print("INT " + place)
      random.shuffle(events['kill'])
      ignore = []
      for tuple in events['kill']:
        if tuple[0] in ignore:
          continue
        print("-" + tuple[0].name + " kills " + tuple[1].name)
        for person in characters:
          if person == tuple[0]:
            person.relationships.pop(tuple[1])
            continue
          if person == tuple[1] or tuple[1] not in person.relationships:
            continue
          if person.relationships[tuple[1]] > 0.5:
            person.relationships[tuple[0]] = -1
            print("-" + person.name + " vowes revenge on " + tuple[0].name)
          elif person.relationships[tuple[1]] > 0:
            change_relationship(person, tuple[0], -0.25)
          if person.relationships[tuple[1]] < -0.5:
            change_relationship(person, tuple[0], 0.25)
          person.relationships.pop(tuple[1])
        if tuple[1] in characters:
          characters.remove(tuple[1])
        ignore.append(tuple[1])
        events['beat up'] = list(filter(lambda x : x[0] != tuple[1] and x[1] != tuple[1], events['beat up']))
        events['insult'] = list(filter(lambda x : x[0] != tuple[1] and x[1] != tuple[1], events['insult']))
        events['converse'] = list(filter(lambda x : x[0] != tuple[1] and x[1] != tuple[1], events['converse']))
      ignore = []
      random.shuffle(events['beat up'])
      for tuple in events['beat up']:
        if tuple[0] in ignore:
          continue
        print("-" + tuple[0].name + " beats up " + tuple[1].name)
        for person in characters:
          if person == tuple[0] or person == tuple[1]:
            continue
          if person.relationships[tuple[1]] > 0.5:
            change_relationship(person, tuple[0], -0.5)
          elif person.relationships[tuple[1]] > 0:
            change_relationship(person, tuple[0], -0.25)
          if person.relationships[tuple[1]] < -0.5:
            change_relationship(person, tuple[0], 0.25)
        tuple[1].relationships[tuple[0]] -= 1
        ignore.append(tuple[1])
        events['insult'] = list(filter(lambda x : x[0] != tuple[1], events['insult']))
        events['converse'] = list(filter(lambda x : x[0] != tuple[1], events['converse']))
      random.shuffle(events['insult'])
      for tuple in events['insult']:
        print("-" + tuple[0].name + " insults " + tuple[1].name)
        change_relationship(tuple[1], tuple[0], -0.25)
        events['insult'] = list(filter(lambda x : x[0] != tuple[1], events['insult']))
        events['converse'] = list(filter(lambda x : x[0] != tuple[1], events['converse']))
      random.shuffle(events['converse'])
      for tuple in events['converse']:
        print("-" + tuple[0].name + " converses with " + tuple[1].name)
        change_relationship(tuple[1], tuple[0], 0.25)
  