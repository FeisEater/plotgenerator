import random
from dataloaders import CharacterDataLoader
from models import Knowledge, Actions, Goal, GoalType
from utilities import safe_append, safe_extend, dump_output

output = []
characters = CharacterDataLoader().load(howmany=10, output=output)
objects = []
step = 0

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
  global characters, output
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
      output.append(source.name + " stole " + object.name)

def do_beat_up(source, target, chars_to_ignore):
  target.relationships[source] -= 1
  chars_to_ignore.append(target)
  source.knowledge = [know for know in source.knowledge if not(know.action == Actions.OWNED_BY and know.target == target)]
  for object in objects:
    if object.owner == target:
      source.knowledge = [know for know in source.knowledge if not(know.action == Actions.LOCATED_IN and know.subject == object)]
      object.owner = source
      object.location = None
      source.goals = [goal for goal in source.goals if goal.target1 != object]
      output.append(source.name + " stole " + object.name)

def do_insult(source, target, chars_to_ignore):
  target.change_relationship(source, -0.25)

def do_converse(source, target, chars_to_ignore):
  target.change_relationship(source, 0.25)
  if source in target.told_knowledge:
    untold_knowledge = [x for x in target.knowledge if x not in target.told_knowledge[source]]
  else:
    untold_knowledge = target.knowledge
  conversation_topics = untold_knowledge if len(untold_knowledge) <= 3 else random.sample(untold_knowledge, 3)
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
    output.append("-" + tuple[0].name + " " + action.value + " " + tuple[1].name)
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

    output.append("At the " + place)
    chars_to_ignore = []
    for action in action_methods.keys():
      execute_action(action, places[place], events, chars_to_ignore)

  dump_output(output)

if __name__ == '__main__':
  dump_output(output)
  while True:
    print("")
    input("Press Enter to progress...")
    print("")
    generation_step()
