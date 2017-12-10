import random
from dataloaders import CharacterDataLoader, ObjectDataLoader
from models import Knowledge, Actions, Goal, GoalType, Location
from utilities import safe_append, safe_extend, persons_shop, TAVERN, dump_output
import output

step = 0
out = []
characters = CharacterDataLoader().load(howmany=10, out=out)
objects = ObjectDataLoader().load(howmany=random.randint(1, 3), random_sample=True, out=out)
locations = [Location(persons_shop(x)) for x in characters] + [Location(TAVERN)]
objectLocations = random.sample(locations, len(objects))
for i in range(len(objects)):
  objects[i].location = objectLocations[i]
  out.append(output.ExposObjectPosition(objects[i], objectLocations[i]))
  pursuerCount = random.randint(1, 3)
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
    
for _ in range(random.randint(0, 3)):
  trio = random.sample(characters, 3)
  trio[0].goals.insert(0, Goal(GoalType.KILL, trio[1], trio[2]))
  out.append(output.ExposManipulationMotivation(trio[0], trio[1], trio[2]))

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

def do_kill(source, target, chars_to_ignore):
  target.dead = True
  global characters, out
  if target in characters:
    characters.remove(target)
  chars_to_ignore.append(target)
  source.knowledge = [know for know in source.knowledge if not(know.action == Actions.OWNED_BY and know.target == target)]
  for object in objects:
    if object.owner == target:
      source.knowledge = [know for know in source.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == object)]
      object.owner = source
      object.location = None
      source.goals = [goal for goal in source.goals if goal.target1 != object]
      out.append(output.Steal(step, source.location, source, target, object))

def do_beat_up(source, target, chars_to_ignore):
  target.change_relationship(source, -1)
  chars_to_ignore.append(target)
  source.knowledge = [know for know in source.knowledge if not(know.action == Actions.OWNED_BY and know.target == target)]
  for object in objects:
    if object.owner == target:
      source.knowledge = [know for know in source.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == object)]
      object.owner = source
      object.location = None
      source.goals = [goal for goal in source.goals if goal.target1 != object]
      out.append(output.Steal(step, source.location, source, target, object))

def do_insult(source, target, chars_to_ignore):
  target.change_relationship(source, -0.25)

def do_converse(source, target, chars_to_ignore):
  target.change_relationship(source, 0.25)
  if source in target.told_knowledge:
    untold_knowledge = [x for x in target.knowledge if x not in target.told_knowledge[source]]
  else:
    untold_knowledge = [x for x in target.knowledge]
  conversation_topics = untold_knowledge if len(untold_knowledge) <= 3 else random.sample(untold_knowledge, 3)
  for topic in conversation_topics:
    topic.source = target
  safe_extend(target.told_knowledge, source, conversation_topics)
  safe_extend(source.told_knowledge, target, conversation_topics)
  for knowledge in conversation_topics:
    source.acquire_knowledge(knowledge)

action_methods = {
  Actions.KILL: do_kill,
  Actions.BEAT_UP: do_beat_up,
  Actions.INSULT: do_insult,
  Actions.CONVERSE: do_converse
}

def execute_action(action, place, events, chars_to_ignore):
  random.shuffle(events[action])
  for tuple in events[action]:
    if tuple[0] in chars_to_ignore:
      continue
    out.append(output.SomeAction(step, tuple[0].location, tuple[0], tuple[1], action))
    if action.is_witnessed:
      for witness in place:
        witness.acquire_knowledge(Knowledge(witness, tuple[0], action, tuple[1], step))
    action_methods[action](tuple[0], tuple[1], chars_to_ignore)
    
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
        events[make_decision(person1, person2)].append((person1, person2))

    chars_to_ignore = []
    for action in action_methods.keys():
      execute_action(action, places[place], events, chars_to_ignore)

  #dump_output(out)

if __name__ == '__main__':
  #dump_output(out)
  for _ in range(25):
    generation_step()
  output.printOutput(out)
