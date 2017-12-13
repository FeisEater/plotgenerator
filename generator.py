import random
from dataloaders import CharacterDataLoader, ObjectDataLoader, LocationDataLoader
from models import Knowledge, Actions, Goal, GoalType, Location
from utilities import safe_append, safe_extend, persons_shop, TAVERN, dump_output
from evaluator import evaluate
import output

class Generator:
  def __init__(self, **kwargs):
    locationCount = kwargs.get("locationCount", 10)
    characterCount = kwargs.get("characterCount", 10)
    objectCount = kwargs.get("objectCount", random.randint(1,4))
    pursuerCount = kwargs.get("pursuerCount", random.randint(1,3))
    adviserCount = kwargs.get("adviserCount", random.randint(1,2))
    redHerringCount = kwargs.get("redHerringCount", random.randint(1,4))
    manipulatorCount = kwargs.get("manipulatorCount", random.randint(0, 7))
    self.iterations = kwargs.get("iterations", 25)

    self.step = 0
    self.out = []
    locations = LocationDataLoader().load(howmany=locationCount, out=self.out)
    self.characters = CharacterDataLoader().load(howmany=characterCount, out=self.out)
    objects = ObjectDataLoader().load(howmany=objectCount, random_sample=True, out=self.out)
    for char in self.characters:
      char.setWorldData(locations, objects)
    objectLocations = random.sample(locations, len(objects))
    for i in range(len(objects)):
      objects[i].location = objectLocations[i]
      self.out.append(output.ExposObjectPosition(objects[i], objectLocations[i]))
      charSample = random.sample(self.characters, pursuerCount + adviserCount + redHerringCount)
      for char in charSample[:pursuerCount]:
        char.goals.insert(0, Goal(GoalType.GET_OBJECT, objects[i]))
        self.out.append(output.ExposOwningMotivation(char, objects[i]))
      for char in charSample[pursuerCount:pursuerCount + adviserCount]:
        locationKnowledge = Knowledge(char, objects[i], Actions.LOCATED_IN, objectLocations[i], -1)
        char.knowledge.append(locationKnowledge)
        self.out.append(output.ExposObjectInfo(char, locationKnowledge, True))
      for char in charSample[pursuerCount + adviserCount:]:
        locale = random.choice(locations)
        locationKnowledge = Knowledge(char, objects[i], Actions.LOCATED_IN, locale, -1)
        char.knowledge.append(locationKnowledge)
        self.out.append(output.ExposObjectInfo(char, locationKnowledge, False))
        
    for _ in range(manipulatorCount):
      trio = random.sample(self.characters, 3)
      trio[0].goals.insert(0, Goal(GoalType.KILL, trio[1], trio[2]))
      self.out.append(output.ExposManipulationMotivation(trio[0], trio[1], trio[2]))

  def execute_action(self, action, place, events, chars_to_ignore):
    random.shuffle(events[action])
    for tuple in events[action]:
      if tuple[0] in chars_to_ignore:
        continue
      methodTuple = tuple[0].action_methods[action](tuple[1], chars_to_ignore)
      context = methodTuple[0]
      additionalOutput = methodTuple[1]
      self.out.append(output.SomeAction(self.step, tuple[0].location, context, tuple[0], tuple[1], action))
      self.out.extend(additionalOutput)
      if action.is_witnessed:
        for witness in place:
          witness.acquire_knowledge(Knowledge(witness, tuple[0], action, tuple[1], self.step))
      
  def generation_step(self):
    self.step += 1
    
    places = {}
    random.shuffle(self.characters)
    for person in list(filter(lambda c: c.dead == False, self.characters)):
      person.schedule_step(self.step)
      safe_append(places, person.location, person)
    self.characters = [c for c in self.characters if c.dead == False]
    
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
      for action in self.characters[0].action_methods.keys():
        self.execute_action(action, places[place], events, chars_to_ignore)

  def run(self, printConsole = False):
    for _ in range(self.iterations):
      self.generation_step()
    protagonist = random.choice(self.characters)
    protagonist.protagonist = True
    score = evaluate(self.out)
    story = output.printOutput(self.out)
    if printConsole:
      for line in story:
        print(line)
      print("Evaluated score: {SCORE}".format(SCORE=score))
    return (story, score)
        