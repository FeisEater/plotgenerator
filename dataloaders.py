from NOCListReader import *
from models import Character
import random
from enum import Enum

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
    def load(self, howmany = None, output = []):
        self.out = output
        data = NOCListReader().get_noc_list_contents()

        characters = self.__parse_characters(data)

        if howmany is not None and isinstance(howmany, int) and howmany > 2:
            characters = random.sample(characters, howmany)

        characters = self.__build_relationships(characters)

        return characters

    def __parse_characters(self, dataframe):
        characters = []

        for index, row in dataframe.iterrows():
            character = Character(name=row[NOCListColumn.CHARACTER_NAME.value], opponent = row[NOCListColumn.OPPONENT.value], output = self.out)

            characters.append(character)

        return characters

    def __build_relationships(self, characters):
        for person in characters:
            for person2 in characters:
                if person == person2:
                    continue
                person.relationships[person2] = random.uniform(-1, 1)
                self.out.append(person.name + " likes " + person2.name + ": " + str(person.relationships[person2]))

        return characters