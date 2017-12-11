import random
import numpy as np
from functools import reduce
import output
from models import Actions

class OverallRelationshipChange:
  def __init__(self, source, target):
    self.source = source # type: Character
    self.target = target # type: Character
    self.change = 0.0 # type: float

  def __repr__(self):
      return "<OverallRelationshipChange {}>".format(self.__str__())

  def __str__(self):
      return "Source: {SOURCE}; Target: {TARGET}; Change: {CHANGE}".format(SOURCE = self.source.name, TARGET = self.target.name, CHANGE = self.change)

def evaluate(story, **kwargs):
    '''
    Evaluates the creativity score of the given story parameter, which is returned by the generator.
    :param story: The story object.
    :type story: [Output]
    :param kwargs: The list of optional parameters as explained below.
        verbose: A boolean indicating if debug information should be printed during the evaluation. Defaults to False.
    :type kwargs: dict
    :return: A score on the range of [0, 1] indicating the value of the story. 1 corresponds to better, while 0 corresponds to worse stories.
    :rtype: float
    '''
    verbose = kwargs.get("verbose", False)

    characters = __get_unique_characters(story)

    scores = [
        __evaluate_characters_variety(characters),
        __evaluate_story_flow(story),
        __evaluate_relationship_changes(story)
    ]

    if verbose:
        print("Scores: {}".format(scores))

    return np.mean(scores)

def __get_unique_characters(story):
    '''
    Extracts the list of characters from the story.
    :param story: The story object.
    :type story: [Output]
    :return: The list of Character that appear in the story.
    :rtype: set
    '''
    characters = set()
    relationships = __get_initial_relationships(story)
    for relationship in relationships:
        characters.add(relationship.source)
        characters.add(relationship.target)

    return characters

def __get_initial_relationships(story):
    '''
    Extracts the list of initial relationships from the story.
    :param story: The story object.
    :type story: [Output]
    :return:
    :rtype: [output.ExposRelationship]
    '''
    relationships = list(filter(lambda x: isinstance(x, output.ExposRelationship), story))
    return relationships

def __evaluate_relationship_changes(story):
    '''
    Determines the score of the list of relationship changes that has happened during the story. The higher score is given if the story has gone through radical changes in terms of character relationships. For instance, if many of the relationships have turned the other way around between characters, if characters have achieved their goals or initial friends have killed eachother in the story, the higher score is given.
    :param story: The story object.
    :type story: [Output]
    :return: A score on the range of [0, 1].
    :rtype: float
    '''
    relationship_changes = list(filter(lambda x: isinstance(x, output.RelationshipChange), story))[:2] # type: [output.RelationshipChange]

    overall_changes = list(map(lambda x: OverallRelationshipChange(source=x.source, target=x.target), __get_initial_relationships(story))) # type: [OverallRelationshipChange]

    for relationship in relationship_changes:
        for change in list(filter(lambda x: x.source == relationship.source and x.target == relationship.target, overall_changes)):
            change.change += relationship.newvalue - relationship.oldvalue

    final_change_values = list(map(lambda x: x.change, overall_changes))
    return np.average(np.abs(final_change_values))

def __evaluate_characters_variety(characters):
    '''
    Evaluates the variety of the characters. The more the characters vary in their talking points and domains, the higher the score is.
    :param characters: The list of Characters that appear in the story.
    :type characters: [Character]
    :return: A score on the range of [0, 1].
    :rtype: float
    '''
    domains = reduce(lambda x, y: x + list(y.domains), characters, [])
    positivite_talking_points = reduce(lambda x, y: x + list(y.positive_talking_points), characters, [])
    negative_talking_points = reduce(lambda x, y: x + list(y.negative_talking_points), characters, [])

    scores = [
        __evaluate_variety_of_strings(domains),
        __evaluate_variety_of_strings(positivite_talking_points),
        __evaluate_variety_of_strings(negative_talking_points)
    ]

    return np.mean(scores)

def __evaluate_variety_of_strings(values):
    '''
    Evaluates the variety of string values.
    :param domains: The list of the strings.
    :type domains: [str]
    :return: A score on the range of [0, 1].
    :rtype: float
    '''
    if len(values) == 0:
        return 0.0
    unique_values = set(values)

    return len(unique_values) / len(values)

def __evaluate_story_flow(story):
    '''
    Evaluates the flow of the story. The function gives higher score if the story starts "slowly" with more neutral actions between characters, which turn into more friendly or violent by the end of the story.
    :param story: The story object.
    :type story: [Output]
    :return: A score on the range of [0, 1].
    :rtype: float
    '''
    interesting_action_types = (output.SomeAction, output.KnowledgeLearned, output.DidntFind, output.Got, output.LieReveal, output.Steal, output.VowRevenge)

    interesting_story_points = __sort_by_time(list(filter(lambda x: isinstance(x, interesting_action_types), story)))
    steps_in_story = __get_number_of_steps_in_story(story)
    scores = []

    for index, event in enumerate(interesting_story_points):
        if isinstance(event, output.SomeAction):
            action_score = __score_action(action = event, total_steps_in_story = steps_in_story)
            scores.append(action_score)
        elif isinstance(event, output.Steal):
            steal_score = __score_steal(steal = event, total_steps_in_story = steps_in_story)
            scores.append(steal_score)

    scores = list(filter(lambda s: s >= 0.0 and s <= 1.0, scores)) # filtering out invalid scores if any
    return np.average(scores)

def __score_action(action, total_steps_in_story):
    '''
    Calculates the score of an action that has happened during the story.
    :param action: The action to be evaluated.
    :type action: output.SomeAction
    :param total_steps_in_story: The total steps/turns that has happened during the story. Must be greater than 0.
    :type total_steps_in_story: int
    :return: A score on the range of [0, 1]. Returns -1 if the action is not handled.
    :rtype: float
    '''
    assert isinstance(action, output.SomeAction)
    assert isinstance(total_steps_in_story, int)
    assert total_steps_in_story > 0

    if action.action == Actions.KILL: # prefer to happen near the end
        return action.time / total_steps_in_story
    elif action.action == Actions.BEAT_UP or action.action == Actions.INSULT: # prefer to happen in the middle
        if action.time <= (total_steps_in_story / 2):
            return action.time / (total_steps_in_story / 2)
        else:
            return - 1 * (1 - (total_steps_in_story / action.time))
    elif action.action == Actions.CONVERSE: # prefer to happen near the beginning
        return (-(action.time - total_steps_in_story) + 1) / total_steps_in_story
    else: # unsure about the action
        return -1

def __score_steal(steal, total_steps_in_story):
    '''
    Calculates the score of an action that has happened during the story.
    :param steal: The steal output to be evaluated.
    :type steal: output.Steal
    :param total_steps_in_story: The total steps/turns that has happened during the story. Must be greater than 0.
    :type total_steps_in_story: int
    :return: A score on the range of [0, 1]. Returns -1 if the action is not handled.
    :rtype: float
    '''
    assert isinstance(steal, output.Steal)
    assert isinstance(total_steps_in_story, int)
    assert total_steps_in_story > 0

    return (-(steal.time - total_steps_in_story) + 1) / total_steps_in_story

def __get_number_of_steps_in_story(story):
    '''
    Gets the number of steps that has happenned in the story. That is, the highest value in the "time" property of all output objects.
    :param story: The story object.
    :type story: [Output]
    :return: The sequential number of the last step in the story.
    :rtype: int
    '''
    return int(np.max(list(map(lambda x: x.time, story))))

def __sort_by_time(story):
    '''
    Sorts the provided story object to chronological order.
    :param story: The story object.
    :type story: [Output]
    :return: The same story ordered by the time value of the items.
    :rtype: [Output]
    '''
    result = sorted(story, key=lambda x: x.time)
    return result