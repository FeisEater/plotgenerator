import random

class Character:
    def __init__(self, name, location = None, opponent = None):
        self.relationships = { opponent: -1 } if isinstance(opponent, str) else {}
        self.name = name
        self.schedule_time = 0
        self.location = location if location is not None else self.name + "'s house"

    def schedule_step(self):
        if self.schedule_time <= 0:
            if self.location == self.name + "s house":
                self.location = self.name + "s shop"
                print(self.name + " goes to " + self.location)
                self.schedule_time = random.randint(2, 8)
            else:
                locations = ["{}s shop".format(x) for x in self.relationships.keys()] + ["tavern", "s house".format(self.name)]
                self.location = random.choice(locations)
                print(self.name + " goes to " + self.location)
                if self.location == self.name + "s house":
                    self.schedule_time = random.randint(2, 8)
                elif self.location == "tavern":
                    self.schedule_time = random.randint(1, 4)
        self.schedule_time -= 1