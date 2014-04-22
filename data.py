class World:
    def __init__(self, data, action):
        self.action = action
        self.data = data

    def diff(self, other):
        return [s for s, o in zip(self.data, other.data) if s != o]

    def sim(self, other):
        return [s for s, o in zip(self.data, other.data) if s == o]

class Cube:
    def __init__(self):
        self.worlds = []

    def record(self, world):
        self.worlds.append(world)
