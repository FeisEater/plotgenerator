import random
import numpy as np

def evaluate(story, **kwargs):
    '''
    Evaluates the creativity score of the given story parameter, which is returned by the generator.
    :param story: The story object.
    :type story:
    :param kwargs: The list of optional parameters as explained below.
        verbose: A boolean indicating if debug information should be printed during the evaluation. Defaults to False.
    :type kwargs: dict
    :return: A score on the range of [0, 1] indicating the value of the story. 1 corresponds to better, while 0 corresponds to worse stories.
    :rtype: float
    '''
    verbose = kwargs.get("verbose", False)

    scores = []

    return np.mean(scores)

def __evaluate_initial_and_final_state(initial_state, final_state):
    '''
    Determines the score between the initial and the final state of the story. The higher score is given if the difference between the two state is "bigger". For instance, if many of the relationships have turned the other way around between characters, if characters have achieved their goals or initial friends have killed eachother in the story, the higher score is given.
    :param initial_state: The dump of the initial state from which the story has begun.
    :type initial_state:
    :param final_state: The dump of the initial state from which the story has ended.
    :type final_state:
    :return: A score on the range of [0, 1].
    :rtype: float
    '''
    return random.uniform(0, 1)

def __evaluate_characters_variety(characters):
    '''
    Evaluates the variety of the characters. The more the characters vary in their talking points and domains, the higher the score is.
    :param characters: The list of Characters that appear in the story.
    :type characters: [Character]
    :return: A score on the range of [0, 1].
    :rtype: float
    '''
    return random.uniform(0, 1)

def __evaluate_story_flow(story):
    '''
    Evaluates the flow of the story. The function gives higher score if the story starts "slowly" with more neutral actions between characters, which turn into more friendly or violent by the end of the story.
    :param story:
    :type story:
    :return: A score on the range of [0, 1].
    :rtype: float
    '''
    return random.uniform(0, 1)