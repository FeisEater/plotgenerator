class Output:
  def __init__(self):
    self.stuff = {}

class ExposRelationship(Output):
  def __init__(self, source, target, value):
    self.source = source
    self.target = target
    self.value = value

class ExposObjectPosition(Output):
  def __init__(self, object, location):
    self.object = object
    self.location = location

class ExposOwningMotivation(Output):
  def __init__(self, subject, object):
    self.subject = subject
    self.object = object

class ExposObjectInfo(Output):
  def __init__(self, source, knowledge, true):
    self.source = source
    self.knowledge = knowledge
    self.true = true

class ExposManipulationMotivation(Output):
  def __init__(self, subject, killer, victim):
    self.subject = subject
    self.killer = killer
    self.victim = victim

class GoesTo(Output):
  def __init__(self, character, place):
    self.character = character
    self.place = place

class Got(Output):
  def __init__(self, character, place):
    self.character = character
    self.place = place

class DidntFind(Output):
  def __init__(self, character, place):
    self.character = character
    self.place = place

class WasLying(Output):
  def __init__(self, source, target, lie):
    self.source = source
    self.target = target
    self.lie = lie

class KnowledgeLearned(Output):
  def __init__(self, learner, knowledge):
    self.learner = learner
    self.knowledge = knowledge

class LieReveal(Output):
  def __init__(self, learner, knowledge):
    self.learner = learner
    self.knowledge = knowledge

class NewInfoIsLie(Output):
  def __init__(self, learner, knowledge):
    self.learner = learner
    self.knowledge = knowledge

class VowRevenge(Output):
  def __init__(self, source, target, victim):
    self.source = source
    self.target = target
    self.victim = victim

class Steal(Output):
  def __init__(self, source, target, object):
    self.source = source
    self.target = target
    self.object = object

class SomeAction(Output):
  def __init__(self, source, target, action):
    self.source = source
    self.target = target
    self.action = action

class Interior(Output):
  def __init__(self, place):
    self.place = place
