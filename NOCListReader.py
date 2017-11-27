from enum import Enum
import pandas as pd

class NOCFile(Enum):
    ANTONYMS = "antonyms.txt"
    CATEGORY_LIST = "category list.txt"
    COMPARATIVES = "comparatives.txt"
    DESSERTS = "List of desserts.txt"
    INGREDIENTS = "List of ingredients.txt"
    PAST_PERFECTS = "past perfects.txt"
    SUPERLATIVES = "superlatives.txt"
    AFFORDANCES = "Veale's affordances.txt"
    CATEGORY_ACTIONS = "Veale's category actions.txt"
    CATEGORY_HIERARCHY = "Veale's Category Hierarchy.txt"
    CLOTHING_LINE = "Veale's clothing line.txt"
    CREATIONS = "Veale's creations.txt"
    DOMAINS = "Veale's domains.txt"
    FICTIONAL_WORLDS = "Veale's fictional worlds.txt"
    INTER_CATEGORY_RELATIONSHIPS = "Veale's Inter-Category Relationships.txt"
    LOCATION_LISTING = "Veale's location listing.txt"
    PLACE_ELEMENTS = "Veale's place elements.txt"
    QUALITY_INVENTORY = "Veale's quality inventory.txt"
    NOC_LIST = "Veale's The NOC List.txt"
    TYPICAL_ACTIVITIES = "Veale's Typical Activities.txt"
    VEHICLE_FLEET = "Veale's vehicle fleet.txt"
    WEAPON_ARSENAL = "Veale's weapon arsenal.txt"
    VERB_LIST = "verb list.txt"

class NOCListReader:
    def __init__(self, path_to_tsv_lists = "The-NOC-List/NOC/DATA/TSV Lists"):
        '''
        Initializes the NOCListReader with the provided parameters.

        :param path_to_tsv_lists: The relative or absolute path to the TSV Lists folder as a string. Defaults to `The-NOC-List/NOC/DATA/TSV Lists`
        :type path_to_tsv_lists: str
        :exception AssertionException if the provided ´path_to_tsv_lists´ is not a string.
        :exception AssertionException if the string is empty.
        '''
        assert isinstance(path_to_tsv_lists, str)
        assert path_to_tsv_lists != ""

        if path_to_tsv_lists.endswith("/") == False:
            path_to_tsv_lists += "/"

        self.path_to_tsv_list = path_to_tsv_lists # type: str

    def get_contents(self, file, separator = "\t"):
        '''
        Reads the contents of the provided file as a pandas DataFrame.

        :param file: The file as a NOCFile clause.
        :type file: NOCFile
        :param separator: The separating character in the file. Defaults to ´\t´
        :type separator: str
        :return: The contents of the file.
        :rtype: pandas.core.frame.DataFrame
        '''
        assert isinstance(file, NOCFile)

        path = self.path_to_tsv_list + file.value
        contents = pd.read_csv(filepath_or_buffer=path, sep=separator, header=True)

        return contents

    def get_noc_list_contents(self):
        '''
        Reads the contents of The NOC List file. Equivalent to get_contents(file = NOCFile.NOC_LIST).
        :return: The contents of The NOC list file.
        :rtype: pandas.core.frame.DataFrame
        '''
        return self.get_contents(file = NOCFile.NOC_LIST)