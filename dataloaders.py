from NOCListReader import *
from proto import Character

class CharacterDataLoader:
    def load(self):
        data = NOCListReader().get_noc_list_contents()

        return self.__parse_characters(data)

    def __parse_characters(self, dataframe):
        characters = []

        for index, row in dataframe.iterrows():
            character = Character(name=row["Character"])

            characters.append(character)

        return characters