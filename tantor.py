import pickle
from data import Cube, World

class Tantor:
    def __init__(self, infns=None):
        self.infns = infns
        self.predictor = None
        self.data = Cube()

    def rec(self, action):
        self.data.record(self.cur(action))

    def cur(self, action=None):
        return World([each() for each in self.infns], action)

    def learn(self, predictor):
        self.predictor = predictor(self.data)

    def predict(self):
        if self.predictor == None:
            print "Error: no predictor."
            return None
        return self.predictor.predict(self.cur())

    def save(self, fn):
        with open(fn, 'w') as file:
            pickle.dump(self.data, file)

    def load(self, fn):
        with open(fn, 'r') as file:
            self.data = pickle.load(file)
