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
  def __init__(self, time, location, context, important=False):
    self.time = time
    self.location = location
    self.context = context
    self.important = important

class ExposRelationship(Output):
  def __init__(self, source, target, value):
    Output.__init__(self, -1, '.', [])
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
    Output.__init__(self, -1, '.', [])
    self.object = object
    self.place = place

  def __str__(self):
    return "{OBJECT} was hidden in {LOCATION}".format(OBJECT=self.object.name, LOCATION=self.place.name)

class ExposOwningMotivation(Output):
  def __init__(self, subject, object):
    Output.__init__(self, -1, '.', [], True)
    self.subject = subject
    self.object = object

  def __str__(self):
    return "Since childhood, {SUBJECT} always wanted to have {OBJECT}".format(OBJECT=self.object.name, SUBJECT=self.subject.name)

class ExposObjectInfo(Output):
  def __init__(self, source, knowledge, trueInfo):
    Output.__init__(self, -1, '.', [])
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
    Output.__init__(self, -1, '.', [], True)
    self.subject = subject
    self.killer = killer
    self.victim = victim

  def __str__(self):
    return "{SUBJECT} thought it'd be fun to see {TARGET} kill {VICTIM}".format(SUBJECT=self.subject.name, TARGET=self.killer.name, VICTIM=self.victim.name)

class GoesTo(Output):
  def __init__(self, time, location, context, character, place, important=False):
    Output.__init__(self, time, location, context, important)
    self.character = character
    self.place = place

  def __str__(self):
    return "{SUBJECT} then decided to go to {LOCATION}".format(SUBJECT=self.character.name, LOCATION=self.place.name)

class Got(Output):
  def __init__(self, time, location, context, character, object):
    Output.__init__(self, time, location, context, True)
    self.character = character
    self.object = object

  def __str__(self):
    return "{SUBJECT} took {OBJECT}".format(SUBJECT=self.character.name, OBJECT=self.object.name)

class DidntFind(Output):
  def __init__(self, time, location, context, character, thing):
    Output.__init__(self, time, location, context, True)
    self.character = character
    self.thing = thing

  def __str__(self):
    return "{SUBJECT} didnt find {OBJECT} in {LOCATION}".format(SUBJECT=self.character.name, OBJECT=self.thing.name, LOCATION=self.location.name)

class WasLying(Output):
  def __init__(self, time, location, context, source, target, lie):
    Output.__init__(self, time, location, context, True)
    self.source = source
    self.target = target
    self.lie = lie

  def __str__(self):
    return "But {SUBJECT} was lying to {TARGET} that '{LIESUBJECT} {ACTION} {LIETARGET}'".format(SUBJECT=self.source.name, TARGET=self.target.name, LIESUBJECT=self.lie.subject.name, ACTION=self.lie.action.value, LIETARGET=self.lie.target.name)

class RelationshipChange(Output):
  def __init__(self, time, location, context, source, target, oldvalue, newvalue, important=False):
    imp = False
    if important and verbalValueOfRelationship(oldvalue) != verbalValueOfRelationship(newvalue):
      imp = True
    Output.__init__(self, time, location, context, imp)
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
  def __init__(self, time, location, context, learner, knowledge):
    important = knowledge.importantKnowledge()
    Output.__init__(self, time, location, context, important)
    self.learner = learner
    self.knowledge = knowledge

  def __str__(self):
    if self.knowledge.source == self.learner:
      return "{CHARACTER} witnessed that {SUBJECT} {ACTION} {TARGET}".format(CHARACTER=self.learner.name, SUBJECT=self.knowledge.subject.name, ACTION=self.knowledge.action.value, TARGET=self.knowledge.target.name)
    return "{CHARACTER} learned from {SOURCE} that {SUBJECT} {ACTION} {TARGET}".format(CHARACTER=self.learner.name, SOURCE=self.knowledge.source.name, SUBJECT=self.knowledge.subject.name, ACTION=self.knowledge.action.value, TARGET=self.knowledge.target.name)

class LieReveal(Output):
  def __init__(self, time, location, context, learner, liar):
    Output.__init__(self, time, location, context, True)
    self.learner = learner
    self.liar = liar

  def __str__(self):
    return "{CHARACTER} then realised that {LIAR} was a liar".format(CHARACTER=self.learner.name, LIAR=self.liar.name)

class NewInfoIsLie(Output):
  def __init__(self, time, location, context, learner, knowledge):
    Output.__init__(self, time, location, context, True)
    self.learner = learner
    self.knowledge = knowledge

  def __str__(self):
    return "But {CHARACTER} didnt believe {LIAR}".format(CHARACTER=self.learner.name, LIAR=self.knowledge.source.name)

class VowRevenge(Output):
  def __init__(self, time, location, context, source, target, victim):
    Output.__init__(self, time, location, context, True)
    self.source = source
    self.target = target
    self.victim = victim

  def __str__(self):
    return "{CHARACTER} vowed revenge on {TARGET} for the death of {VICTIM}".format(CHARACTER=self.source.name, TARGET=self.target.name, VICTIM=self.victim.name)

class Steal(Output):
  def __init__(self, time, location, context, source, target, object):
    Output.__init__(self, time, location, context, True)
    self.source = source
    self.target = target
    self.object = object

  def __str__(self):
    return "{CHARACTER} stole {OBJECT} from the {TARGET}'s body".format(CHARACTER=self.source.name, TARGET=self.target.name, OBJECT=self.object.name)

class SomeAction(Output):
  def __init__(self, time, location, context, source, target, action):
    important = action.importantEvent
    Output.__init__(self, time, location, context, important)
    self.source = source
    self.target = target
    self.action = action

  def __str__(self):
    return "{CHARACTER} {ACTION} {TARGET}".format(CHARACTER=self.source.name, TARGET=self.target.name, ACTION=self.action.value)

class Context:
  def __init__(self, outputType, attrDict):
    self.outputType = outputType
    self.attrDict = attrDict

def attrMatch(object, nestedattr, value):
  attrs = nestedattr.split('.')
  tempObject = object
  for attr in attrs:
    tempObject = getattr(tempObject, attr)
  return tempObject == value

def revealContext(output, maxIdx, context):
  for idx, line in enumerate(output[:maxIdx]):
    if type(line) is context.outputType:
      match = True
      for attr in context.attrDict:
        if not attrMatch(line, attr, context.attrDict[attr]):
          match = False
      if match and not line.important:
        line.important = True
        for context in line.context:
          revealContext(output, idx, context)

def printOutput(output):
  result = []
  output.sort(key=attrgetter('time'))
  prevLocation = None
  prevTime = -1
  
  characters = [out.source for out in output if type(out) is ExposRelationship] + [out.target for out in output if type(out) is ExposRelationship]
  characters = list(set(characters))
  
  for line in output:
    if type(line) is GoesTo and line.character.protagonist:
      line.important = True

  for idx, line in enumerate(output):
    if line.important:
      for context in line.context:
        revealContext(output, idx, context)

  protagonist = [char for char in characters if char.protagonist][0]
  protagonistLocation = [out.location for out in output if type(out) is GoesTo and out.character == protagonist][0]
  printLocation = True
  for line in output:
    if line.location != prevLocation:
      printLocation = True
    if line.important:
      if printLocation:
        if line.location == '.':
          result.append("This is a story about {PROTAGONIST}".format(PROTAGONIST=protagonist.name))
        elif line.location == protagonistLocation:
          result.append("\nAt the {LOCATION}...".format(LOCATION=line.location))
        else:
          result.append("\nMeanwhile, at the {LOCATION}...".format(LOCATION=line.location))        
        prevLocation = line.location
      result.append(line)
      printLocation = False
      printTime = False
    if type(line) is GoesTo and line.character == protagonist:
      protagonistLocation = line.place
  return result

