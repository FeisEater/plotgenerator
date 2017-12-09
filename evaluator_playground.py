import evaluator
from dataloaders import CharacterDataLoader, ObjectDataLoader, NOCListDomain

#characters = CharacterDataLoader().load(howmany=10)
characters = CharacterDataLoader().load(howmany=10, domain=NOCListDomain.THE_SIMPSONS)

print(characters)
evaluator.__evaluate_characters_variety(characters)