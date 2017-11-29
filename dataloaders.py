from NOCListReader import *
from models import Character
import random

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
            character = Character(name=row["Character"], opponent = row["Opponent"], output = self.out)

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