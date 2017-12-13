import operator, sys, random
from generator import Generator

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print("Usage: second argument specifies amount of generation iterations, third argument specifies filename")
    print("Example: python generator.py 20 result.txt")
  iterations = int(sys.argv[1])
  stories = []
  for i in range(iterations):
    print("story " + str(i))
    characterCount = random.randint(5, 12)
    try:
      gen = Generator(locationCount=characterCount + random.randint(-2,2), characterCount=characterCount, manipulatorCount=random.randint(0,6), iterations=random.randint(15, 35))
      stories.append(gen.run())
    except:
      print("Problem...")
      continue
  stories.sort(key=operator.itemgetter(1), reverse=True)
  with open(sys.argv[2], "w+") as f:
    for story in stories:
      for line in story[0]:
        f.write(line.__str__() + '\n')
      f.write("\nStory evaluated as {SCORE}\n".format(SCORE=story[1]))
      f.write("\n------------------------\n\n")
