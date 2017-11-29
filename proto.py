import random
from dataloaders import CharacterDataLoader
from models import Knowledge
        
def safe_append(dict, key, value):
  if key not in dict:
    dict[key] = [value]
  else:
    dict[key].append(value)
    
if __name__ == '__main__':
  output = []
  characters = CharacterDataLoader().load(howmany=10, output=output)
  for msg in output:
    print(msg)
  del output[:]
  
  step = 0
  while True:
    step += 1
    print("")
    input("Press Enter to progress...")
    print("")
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
      output.append("INT " + place)
      random.shuffle(events['kill'])
      ignore = []
      for tuple in events['kill']:
        if tuple[0] in ignore:
          continue
        output.append("-" + tuple[0].name + " kills " + tuple[1].name)
        for witness in places[place]:
          witness.acquire_knowledge(Knowledge(tuple[0], "killed", tuple[1], step))
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
        output.append("-" + tuple[0].name + " beats up " + tuple[1].name)
        for witness in places[place]:
          witness.acquire_knowledge(Knowledge(tuple[0], "beat up", tuple[1], step))
        tuple[1].relationships[tuple[0]] -= 1
        ignore.append(tuple[1])
        events['insult'] = list(filter(lambda x : x[0] != tuple[1], events['insult']))
        events['converse'] = list(filter(lambda x : x[0] != tuple[1], events['converse']))
      random.shuffle(events['insult'])
      for tuple in events['insult']:
        output.append("-" + tuple[0].name + " insults " + tuple[1].name)
        tuple[1].change_relationship(tuple[0], -0.25)
        events['insult'] = list(filter(lambda x : x[0] != tuple[1], events['insult']))
        events['converse'] = list(filter(lambda x : x[0] != tuple[1], events['converse']))
      random.shuffle(events['converse'])
      for tuple in events['converse']:
        output.append("-" + tuple[0].name + " converses with " + tuple[1].name)
        tuple[1].change_relationship(tuple[0], 0.25)
        for knowledge in tuple[1].knowledge:
          tuple[0].acquire_knowledge(knowledge)
    for msg in output:
      print(msg)
    del output[:]