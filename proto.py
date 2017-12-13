import random
from dataloaders import CharacterDataLoader, ObjectDataLoader, LocationDataLoader
from models import Knowledge, Actions, Goal, GoalType, Location
from utilities import safe_append, safe_extend, persons_shop, TAVERN, dump_output
import output

step = 0
out = []
locations = LocationDataLoader().load(howmany=10, out=out)
characters = CharacterDataLoader().load(howmany=10, out=out)
objects = ObjectDataLoader().load(howmany=random.randint(1, 3), random_sample=True, out=out)
for char in characters:
  char.setWorldData(locations, objects)
objectLocations = random.sample(locations, len(objects))
for i in range(len(objects)):
  objects[i].location = objectLocations[i]
  out.append(output.ExposObjectPosition(objects[i], objectLocations[i]))
  pursuerCount = random.randint(1, 4)
  adviserCount = random.randint(1, 2)
  redHerringCount = random.randint(1, 4)
  charSample = random.sample(characters, pursuerCount + adviserCount + redHerringCount)
  for char in charSample[:pursuerCount]:
    char.goals.insert(0, Goal(GoalType.GET_OBJECT, objects[i]))
    out.append(output.ExposOwningMotivation(char, objects[i]))
  for char in charSample[pursuerCount:pursuerCount + adviserCount]:
    locationKnowledge = Knowledge(char, objects[i], Actions.LOCATED_IN, objectLocations[i], -1)
    char.knowledge.append(locationKnowledge)
    out.append(output.ExposObjectInfo(char, locationKnowledge, True))
  for char in charSample[pursuerCount + adviserCount:]:
    locale = random.choice(locations)
    locationKnowledge = Knowledge(char, objects[i], Actions.LOCATED_IN, locale, -1)
    char.knowledge.append(locationKnowledge)
    out.append(output.ExposObjectInfo(char, locationKnowledge, False))
    
for _ in range(random.randint(0, 7)):
  trio = random.sample(characters, 3)
  trio[0].goals.insert(0, Goal(GoalType.KILL, trio[1], trio[2]))
  out.append(output.ExposManipulationMotivation(trio[0], trio[1], trio[2]))

def execute_action(action, place, events, chars_to_ignore):
  random.shuffle(events[action])
  for tuple in events[action]:
    if tuple[0] in chars_to_ignore:
      continue
    methodTuple = tuple[0].action_methods[action](tuple[1], chars_to_ignore)
    context = methodTuple[0]
    additionalOutput = methodTuple[1]
    out.append(output.SomeAction(step, tuple[0].location, context, tuple[0], tuple[1], action))
    out.extend(additionalOutput)
    if action.is_witnessed:
      for witness in place:
        witness.acquire_knowledge(Knowledge(witness, tuple[0], action, tuple[1], step))
    
def generation_step():
  global step
  global characters
  
  step += 1
  
  places = {}
  random.shuffle(characters)
  for person in list(filter(lambda c: c.dead == False, characters)):
    person.schedule_step(step)
    safe_append(places, person.location, person)
  characters = [c for c in characters if c.dead == False]
  
  for place in places:
    events = {}
    for action in Actions:
      events[action] = []

    for person1 in places[place]:
      for person2 in places[place]:
        if person1 == person2:
          continue
        events[person1.make_decision(person2)].append((person1, person2))

    chars_to_ignore = []
    for action in characters[0].action_methods.keys():
      execute_action(action, places[place], events, chars_to_ignore)

  #dump_output(out)

if __name__ == '__main__':
  #dump_output(out)
  for _ in range(25):
    generation_step()
  protagonist = random.choice(characters)
  protagonist.protagonist = True
  output.printOutput(out)
