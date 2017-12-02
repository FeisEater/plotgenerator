from NOCListReader import *
from models import Character
import random
from enum import Enum
import numpy as np

class NOCListColumn(Enum):
    CHARACTER_NAME = "Character"
    CANONICAL_NAME = 'Canonical Name'
    GENDER = 'Gender'
    DISTRICT = 'Address 1'
    CITY = 'Address 2'
    COUNTRY = 'Address 3'
    POLITICS = 'Politics'
    MARTIAL_STATUS = 'Marital Status'
    OPPONENT = 'Opponent'
    TYPICAL_ACTIVITY = 'Typical Activity'
    VEHICLE_OF_CHOICE = 'Vehicle of Choice'
    WEAPON_OF_CHOICE = 'Weapon of Choice'
    SEEN_WEARING = 'Seen Wearing'
    DOMAINS = 'Domains'
    GENRES = 'Genres'
    FICTIVE_STATUS = 'Fictive Status'
    PORTRAYED_BY = 'Portrayed By'
    CREATOR = 'Creator'
    CREATION = 'Creation'
    GROUP_AFFILIATION = 'Group Affiliation'
    FICTIONAL_WORLD = 'Fictional World'
    CATEGORY = 'Category'
    NEGATIVE_TALKING_POINTS = 'Negative Talking Points'
    POSITIVE_TALKING_POINTS = 'Positive Talking Points'

class CharacterDataLoader:
    def load(self, howmany = None, random_sample = True, output = []):
        self.out = output
        data = NOCListReader().get_noc_list_contents()

        characters = self.__parse_characters(data)

        if howmany is not None and isinstance(howmany, int) and howmany > 2:
            if random_sample:
                characters = random.sample(characters, howmany)
            else:
                characters = characters[:howmany]

        characters = self.__build_relationships(characters, data)

        return characters

    def __parse_characters(self, data):
        '''
        Parses the characters into a list of Character objects from the NOC list.
        :param data: The NOC List as a pandas DataFrame.
        :type data: pandas.core.Frame.DataFrame
        :return: The list of Characters extracted from the data.
        :rtype: [Character]
        '''
        characters = []

        for index, row in data.iterrows():
            character = Character(name=row[NOCListColumn.CHARACTER_NAME.value], positive_talking_points=self.__extract_talking_points(row[NOCListColumn.POSITIVE_TALKING_POINTS.value]), negative_talking_points=self.__extract_talking_points(row[NOCListColumn.NEGATIVE_TALKING_POINTS.value]), output = self.out)

            characters.append(character)

        return characters

    def __build_relationships(self, characters, data):
        '''
        Initializes the relationships between the list of characters using the
        :param characters: The list of Characters.
        :type characters: [Character]
        :param data: The NOC List as a pandas DataFrame.
        :type data: pandas.core.Frame.DataFrame
        :return: The original list of Characters but with configured relationship dictionaries.
        :rtype: [Character]
        '''
        for person in characters:
            for person2 in characters:
                if person == person2 or self.__have_relationship(person, person2):
                    continue

                if self.__are_opponents(person, person2, data):
                    person.relationships[person2] = -1.0
                    person2.relationships[person] = -1.0
                else:
                    positive_union = person.positive_talking_points.union(person2.positive_talking_points)
                    negative_union = person.negative_talking_points.union(person2.negative_talking_points)
                    positive_intersection = person.positive_talking_points.intersection(person2.positive_talking_points)
                    negative_intersection = person.negative_talking_points.intersection(person2.negative_talking_points)

                    scores = [len(positive_intersection) / len(positive_union), len(negative_intersection) / len(negative_union)]

                    person.relationships[person2] = np.average(scores)
                    # person.relationships[person2] = random.uniform(-1, 1)
                    # person2.relationships[person] = random.uniform(-1, 1)
                self.out.append(person.name + " likes " + person2.name + ": " + str(person.relationships[person2]))

        return characters

    def __have_relationship(self, person1, person2):
        '''
        Tells if two characters have a two-way between eachother.
        :param person1: The first character.
        :type person1: Character
        :param person2: The second character.
        :type person2: Character
        :return: True, if a two-way relationship exist. False otherwise.
        :rtype: bool
        '''
        return person2 in person1.relationships.keys() and person1 in person2.relationships.keys()

    def __are_opponents(self, person1, person2, data):
        '''
        Tells if two characters are opponents.
        :param person1: The first character.
        :type person1: Character
        :param person2: The second character.
        :type person2: Character
        :param data: The data extracted from the NOC list as a pandas DataFrame.
        :type data: pandas.core.Frame.DataFrame
        :return: True, if the two characters are opponents. False otherwise.
        :rtype: bool
        '''
        if person2.name in data[data[NOCListColumn.OPPONENT.value] == person1.name][NOCListColumn.CHARACTER_NAME.value].values:
            return True
        else:
            return False

    def __extract_talking_points(self, column_value):
        values = str(column_value).split(",")
        values = set(map(lambda x: x.strip(), values))

        return values