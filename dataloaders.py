from NOCListReader import *
from models import Object, Location
from character import Character
import random
from enum import Enum
import numpy as np
import math
import output

class NOCListColumn(Enum):
    '''An enumeration that holds the column headers of the NOC List dataset.'''
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

class NOCListDomain(Enum):
    '''An enumeration that holds some of character domain values in the NOC List dataset.'''
    HOLLYWOOD = "Hollywood"
    ACTING = "Acting"
    COMEDY = "Comedy"
    AMERICAN_POLITICS = "American politics"
    THE_SIMPSONS = "The Simpsons"
    SPRINGFIELD = "Springfield"
    POP_MUSIC = "Pop music"
    MARVEL = "Marvel"
    COMICS = "Comics"
    VICTORIAN_LITERATURE = "Victorian literature"

class NOCWeaponArsenalColumn(Enum):
    DETERMINER = "Determiner"
    WEAPON = "Weapon"
    AFFORDANCES = "Affordances"

class NOCLocationListingColumn(Enum):
    NAME = "Location"
    TYPE = "Type"
    DETERMINER = "Determiner"
    PREPOSITION = "Preposition"
    SIZE = "Size"
    AMBIENCE = "Ambience"
    INTERACTIONS = "Interactions"
    PROPS = "Props"

class DataLoader:
    def _sample(self, data, howmany, random_sample):
        if howmany is not None and isinstance(howmany, int) and howmany > 0:
            if random_sample:
                data = random.sample(data, howmany)
            else:
                data = data[:howmany]
        return data

class CharacterDataLoader(DataLoader):
    '''A class that can parse the NOC List characters into the local Character object type'''
    def load(self, howmany = None, random_sample = True, domain = None, out = []):
        '''
        Loads Characters from the NOC list.
        :param howmany: An integer indicating how many characters to load or None if all of them should be loaded. Must be greater than 2. Defaults to None.
        :type howmany: int
        :param random_sample: A boolean indicating if a random sample of characters should be loaded. If set to false, the parsing begins from the beginning of the file. Defaults to True.
        :type random_sample: bool
        :param domain: The domain from which characters should be loaded or None, if characters across domains are desired. Defaults to None.
        :type domain: NOCListDomain
        :param out:
        :type out:
        :return: The list of Character objects loaded from the NOC List with the given parameters.
        :rtype: [Character]
        '''
        assert domain is None or isinstance(domain, NOCListDomain)

        self.out = out
        data = NOCListReader().get_noc_list_contents()

        if domain is not None:
            data = data[data[NOCListColumn.DOMAINS.value].str.contains(domain.value)]

        characters = self.__parse_characters(data)
        characters = self._sample(characters, howmany, random_sample)

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
            character = Character(
                name=row[NOCListColumn.CHARACTER_NAME.value],
                positive_talking_points=self.__extract_set_of_strings(row[NOCListColumn.POSITIVE_TALKING_POINTS.value]),
                negative_talking_points=self.__extract_set_of_strings(row[NOCListColumn.NEGATIVE_TALKING_POINTS.value]),
                political_views=self.__extract_set_of_strings(row[NOCListColumn.POLITICS.value]),
                domains = self.__extract_set_of_strings(row[NOCListColumn.DOMAINS.value]),
                out = self.out
            )

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
                    person.relationships[person2] = np.average([self.__get_initial_relationship_from_political_views(person, person2), self.__get_initial_relationship_from_talking_points(person, person2), random.uniform(-.5, .5)])
                    person2.relationships[person] = np.average([self.__get_initial_relationship_from_political_views(person2, person), self.__get_initial_relationship_from_talking_points(person2, person), random.uniform(-.5, .5)])

                self.out.append(output.ExposRelationship(person, person2, person.relationships[person2]))

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

    def __extract_set_of_strings(self, column_value):
        if column_value is None or not isinstance(column_value, str):
            return set()

        values = str(column_value).split(",")
        values = list(filter(lambda s: s != "" and s is not None, values)) # filtering out empty strings
        values = set(map(lambda x: x.strip(), values))

        return values

    def __get_initial_relationship_from_talking_points(self, person, person2):
        positive_union = person.positive_talking_points.union(person2.positive_talking_points)
        negative_union = person.negative_talking_points.union(person2.negative_talking_points)
        positive_intersection = person.positive_talking_points.intersection(person2.positive_talking_points)
        negative_intersection = person.negative_talking_points.intersection(person2.negative_talking_points)
        
        scores = [len(positive_intersection) / len(positive_union), len(negative_intersection) / len(negative_union)]
        
        return np.average(scores) # -0.5 # the substractions is an offset to generate more extreme initial relationship

    def __get_initial_relationship_from_political_views(self, person, person2):
        positive_union = person.political_views.union(person2.political_views)
        negative_union = person.political_views.union(person2.political_views)
        positive_intersection = person.political_views.intersection(person2.political_views)
        negative_intersection = person.political_views.intersection(person2.political_views)

        positive_score = len(positive_intersection) / len(positive_union) if len(positive_union) != 0 else 0
        negative_score = len(negative_intersection) / len(negative_union) if len(negative_union) != 0 else 0

        scores = [positive_score, negative_score]
    
        return np.average(scores) -0.5 # the substractions is an offset to generate more extreme initial relationship

class ObjectDataLoader(DataLoader):
    def load(self, howmany = None, random_sample = True, out = []):
        self.out = out

        data = NOCListReader().get_weapon_arsenal_contents()
        
        objects = self.__parse_objects(data)
        objects = self._sample(data = objects, howmany = howmany, random_sample = random_sample)

        return objects
    
    def __parse_objects(self, data):
        objects = []

        for index, row in data.iterrows():
            object = Object(name=row[NOCWeaponArsenalColumn.WEAPON.value])

            objects.append(object)

        return objects

class LocationDataLoader(DataLoader):
    def load(self, howmany = None, random_sample = True, out = []):
        self.out = out

        data = NOCListReader().get_location_listing_contents()

        objects = self.__parse_objects(data)
        objects = self._sample(data=objects, howmany=howmany, random_sample=random_sample)

        return objects

    def __parse_objects(self, data):
        objects = []

        for index, row in data.iterrows():
            object = Location(name=row[NOCLocationListingColumn.NAME.value])

            objects.append(object)

        return objects