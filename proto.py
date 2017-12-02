import random
from dataloaders import CharacterDataLoader
from models import Knowledge
from enum import Enum
from library import Actions

output = []
characters = CharacterDataLoader().load(howmany=10, output=output)
step = 0

def safe_append(dict, key, value):
  if key not in dict:
    dict[key] = [value]
  else:
    dict[key].append(value)

def dump_output():
  global output
  for msg in output:
    print(msg)
  del output[:]

def make_decision(source, target):
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
  global characters
  if target in characters:
    characters.remove(target)
  chars_to_ignore.append(target)

def do_beat_up(source, target, chars_to_ignore):
  target.relationships[source] -= 1
  chars_to_ignore.append(target)

def do_insult(source, target, chars_to_ignore):
  target.change_relationship(source, -0.25)

def do_converse(source, target, chars_to_ignore):
  target.change_relationship(source, 0.25)
  for knowledge in target.knowledge:
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
        witness.acquire_knowledge(Knowledge(tuple[0], action, tuple[1], step))
    action_methods[action](tuple[0], tuple[1], chars_to_ignore)
    
def generation_step():
  global step
  global characters
  
  step += 1
  
  places = {}
  for person in characters:
    person.schedule_step()
    safe_append(places, person.location, person)
  
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
    for action in Actions:
      if action != Actions.NONE:
        execute_action(action, places[place], events, chars_to_ignore)

  dump_output()

if __name__ == '__main__':
  dump_output()
  while True:
    print("")
    input("Press Enter to progress...")
    print("")
    generation_step()
