# plotgenerator

The main goal of this project is to create the basis of a system which can generate plot skeleton of a book, movie or a fictional story. The output is a readable, sequential list of events that happen in the story. The output is generated in English. The generated stories are comprehensive and are easily readable without technical background. Project includes an evaluator, which rewards stories that get more exciting towards the end. The system generates stories using existing characters (living or dead, fictional or real) and their traits/characteristics. Characters of a new stories are not necessarily tied to a domain, hence it might happen that the system’s stories are told about George Washington and Han Solo venturing together.

Generation is done by defining a set of characters and locations. Characters have different goals, either acquiring some object, manipulating other characters into hating each other, or just wandering around. Character interaction is simulating in a turn-based system. Characters interact with each other based on their individual knowledge base.

The initial knowledge base about the characters is gathered using The NOC List. The initial relationships between characters that are used for the stories can be generated based on the same database, as it contains data about the opponents/enemies of characters. Relationships between characters that are from different domains are randomized or calculated based on how similar the characters appear to be in the database. The relationships change over time dynamically as the story is generated.

# Instructions

To simply generate a story, go to python IDLE from project directory and do following:

Load generator class code:
> exec(open('generator.py').read())

Initialize generator object:
> gen = Generator()

Run generator (setting argument to True will print story to console. x holds the story as array and the evaluated score):
> x = gen.run(True)

Generator constructors takes the following kwargs (each parameter is integer):
* locationCount: amount of locations in the story
* characterCount: amount of characters in the story
* objectCount: amount of mcguffins in the story
* pursuerCount: amount of characters whose motivation is to get some mcguffins
* adviserCount: amount of characters that know where some mcguffin is hidden
* redHerringCount: amount of characters that think they know where some mcguffin is hidden
* manipulatorCount: amount of characters that want to manipulate some character into killing another character
* iterations: amount of steps to generate in the simulation

Example: gen = Generator(characterCount=9, iterations=12)

You can also run a massive generation of stories ordered by their evaluated score from command line:
> python plot.py n filename

Where n is amount of stories and filename is the name of the file where the stories will be written

# Resources
[Scealextric](https://github.com/prosecconetwork/Scealextric)

[The-NOC-List](https://github.com/prosecconetwork/The-NOC-List)

# Blogs, scientific papers, references
[Nicolle Cysneiros: Graph Databases: Talking about your Data Relationships with Python](https://medium.com/labcodes/graph-databases-talking-about-your-data-relationships-with-python-b438c689dc89)

[Michael Brenner: Dynamic Plot Generation by Continual Multiagent Planning](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.217.3084&rep=rep1&type=pdf)

[Prosecco network](http://www.prosecco-network.eu/)

[Veale, T. (2016). A Rap on the Knuckles and a Twist in the Tale: From Tweeting Affective Metaphors to Generating Stories with a Moral](https://www.aaai.org/ocs/index.php/SSS/SSS16/paper/download/12718/11961)

[Veale, T. (2017). Déjà Vu All Over Again On the Creative Value of Familiar Elements in the Telling of Original Tales](http://afflatus.ucd.ie/Papers/Deja%20Vu.pdf)
