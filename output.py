from operator import attrgetter

def verbalValueOfRelationship(x):
  if x < -0.75:
    return -3
  if x < -0.5:
    return -2
  if x < -0.25:
    return -1
  if x < 0:
    return 0
  if x < 0.25:
    return 1
  if x < 0.5:
    return 2
  if x < 0.75:
    return 3
  return 4

class Output:
  def __init__(self, time, location, important=False):
    self.time = time
    self.location = location
    self.important = important

class ExposRelationship(Output):
  def __init__(self, source, target, value):
    Output.__init__(self, -1, '.')
    self.source = source
    self.target = target
    self.value = value
  
  def __str__(self):
    verbal = {
      -3: "had a vendetta against",
      -2: "hated",
      -1: "disliked",
      0: "was annoyed by",
      1: "had no opinion of",
      2: "was fond of",
      3: "liked",
      4: "loved"
    }
    relationship = verbal[verbalValueOfRelationship(self.value)]
    return "{SOURCE} {RELATIONSHIP} {TARGET}".format(SOURCE=self.source.name, RELATIONSHIP=relationship, TARGET=self.target.name)

class ExposObjectPosition(Output):
  def __init__(self, object, place):
    Output.__init__(self, -1, '.')
    self.object = object
    self.place = place

  def __str__(self):
    return "{OBJECT} was hidden in {LOCATION}".format(OBJECT=self.object.name, LOCATION=self.place.name)

class ExposOwningMotivation(Output):
  def __init__(self, subject, object):
    Output.__init__(self, -1, '.', True)
    self.subject = subject
    self.object = object

  def __str__(self):
    return "Since childhood, {SUBJECT} always wanted to have {OBJECT}".format(OBJECT=self.object.name, SUBJECT=self.subject.name)

class ExposObjectInfo(Output):
  def __init__(self, source, knowledge, trueInfo):
    Output.__init__(self, -1, '.')
    self.source = source
    self.knowledge = knowledge
    self.trueInfo = trueInfo

  def __str__(self):
    if self.trueInfo:
      return "{SUBJECT} knew that {OBJECT} was hidden in {LOCATION}".format(OBJECT=self.knowledge.subject.name, SUBJECT=self.source.name, LOCATION=self.knowledge.target.name)
    else:
      return "{SUBJECT} thought in err that {OBJECT} was hidden in {LOCATION}".format(OBJECT=self.knowledge.subject.name, SUBJECT=self.source.name, LOCATION=self.knowledge.target.name)
    
class ExposManipulationMotivation(Output):
  def __init__(self, subject, killer, victim):
    Output.__init__(self, -1, '.', True)
    self.subject = subject
    self.killer = killer
    self.victim = victim

  def __str__(self):
    return "{SUBJECT} thought it'd be fun to see {TARGET} kill {VICTIM}".format(SUBJECT=self.subject.name, TARGET=self.killer.name, VICTIM=self.victim.name)

class GoesTo(Output):
  def __init__(self, time, location, character, place, important=False):
    Output.__init__(self, time, location, important)
    self.character = character
    self.place = place

  def __str__(self):
    return "{SUBJECT} then decided to go to {LOCATION}".format(SUBJECT=self.character.name, LOCATION=self.place.name)

class Got(Output):
  def __init__(self, time, location, character, object):
    Output.__init__(self, time, location, True)
    self.character = character
    self.object = object

  def __str__(self):
    return "{SUBJECT} took {OBJECT}".format(SUBJECT=self.character.name, OBJECT=self.object.name)

class DidntFind(Output):
  def __init__(self, time, location, character, thing):
    Output.__init__(self, time, location, True)
    self.character = character
    self.thing = thing

  def __str__(self):
    return "{SUBJECT} didnt find {OBJECT} in {LOCATION}".format(SUBJECT=self.character.name, OBJECT=self.thing.name, LOCATION=self.location.name)

class WasLying(Output):
  def __init__(self, time, location, source, target, lie):
    Output.__init__(self, time, location, True)
    self.source = source
    self.target = target
    self.lie = lie

  def __str__(self):
    return "But {SUBJECT} was lying to {TARGET} about {LIE}".format(SUBJECT=self.source.name, TARGET=self.target.name, LIE=self.lie.action.value)

class RelationshipChange(Output):
  def __init__(self, time, location, source, target, oldvalue, newvalue, important=False):
    imp = False
    if important and verbalValueOfRelationship(oldvalue) != verbalValueOfRelationship(newvalue):
      imp = True
    Output.__init__(self, -1, None, imp)
    self.source = source
    self.target = target
    self.oldvalue = oldvalue
    self.newvalue = newvalue

  def __str__(self):
    verbal = {
      -3: "had a vendetta against",
      -2: "hated",
      -1: "disliked",
      0: "was annoyed by",
      1: "had no opinion of",
      2: "was fond of",
      3: "liked",
      4: "loved"
    }
    relationship = verbal[verbalValueOfRelationship(self.newvalue)]
    return "{SOURCE} now {RELATIONSHIP} {TARGET}".format(SOURCE=self.source.name, RELATIONSHIP=relationship, TARGET=self.target.name)

class KnowledgeLearned(Output):
  def __init__(self, time, location, learner, knowledge):
    important = knowledge.importantKnowledge()
    Output.__init__(self, time, location, important)
    self.learner = learner
    self.knowledge = knowledge

  def __str__(self):
    return "{CHARACTER} learned from {SOURCE} that {SUBJECT} {ACTION} {TARGET}".format(CHARACTER=self.learner.name, SOURCE=self.knowledge.source.name, SUBJECT=self.knowledge.subject.name, ACTION=self.knowledge.action.value, TARGET=self.knowledge.target.name)

class LieReveal(Output):
  def __init__(self, time, location, learner, liar):
    Output.__init__(self, time, location, True)
    self.learner = learner
    self.liar = liar

  def __str__(self):
    return "{CHARACTER} then realised that {LIAR} was a liar".format(CHARACTER=self.learner.name, LIAR=self.liar.name)

class NewInfoIsLie(Output):
  def __init__(self, time, location, learner, knowledge):
    Output.__init__(self, time, location, True)
    self.learner = learner
    self.knowledge = knowledge

  def __str__(self):
    return "But {CHARACTER} didnt believe {LIAR}".format(CHARACTER=self.learner.name, LIAR=self.knowledge.source.name)

class VowRevenge(Output):
  def __init__(self, time, location, source, target, victim):
    Output.__init__(self, time, location, True)
    self.source = source
    self.target = target
    self.victim = victim

  def __str__(self):
    return "{CHARACTER} vowed revenge on {TARGET} for the death of {VICTIM}".format(CHARACTER=self.source.name, TARGET=self.target.name, VICTIM=self.victim.name)

class Steal(Output):
  def __init__(self, time, location, source, target, object):
    Output.__init__(self, time, location, True)
    self.source = source
    self.target = target
    self.object = object

  def __str__(self):
    return "{CHARACTER} stole {OBJECT} from the {TARGET}'s body".format(CHARACTER=self.source.name, TARGET=self.target.name, OBJECT=self.object.name)

class SomeAction(Output):
  def __init__(self, time, location, source, target, action):
    important = action.importantEvent
    Output.__init__(self, time, location, important)
    self.source = source
    self.target = target
    self.action = action

  def __str__(self):
    return "{CHARACTER} {ACTION} {TARGET}".format(CHARACTER=self.source.name, TARGET=self.target.name, ACTION=self.action.value)

def printOutput(output):
  output.sort(key=attrgetter('time'))
  prevLocation = None
  prevTime = -1
  
  print("Debug output with unimportant fluff\n")
  for line in output:
    if line.time != prevTime:
      print("\n***\n")
      prevTime = line.time
      prevLocation = '.'
    if line.location != prevLocation:
      print("\nAt the {LOCATION}...".format(LOCATION=line.location))
      prevLocation = line.location
    print(line)

  print("\nNow, filtered output:\n")
  printLocation = True
  printTime = True
  for line in output:
    if line.time != prevTime:
      printTime = True
    if line.location != prevLocation:
      printLocation = True
    if line.important:
      if printTime:
        print("\n***\n")
        prevTime = line.time
        prevLocation = '.'
      if printLocation:
        print("\nAt the {LOCATION}...".format(LOCATION=line.location))
        prevLocation = line.location
      print(line)
      printLocation = False
      printTime = False

