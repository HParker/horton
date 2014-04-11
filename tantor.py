from __future__ import division
import itertools
import operator
import pickle
import code
import random

class Tantor:
    """
    Create a datacube that stores a set of actions
    and the state of the world at the time of that action.
    """
    def __init__(self, inputs):
        self.predictor = None
        self.actions = []
        self.inputs = inputs
        self.worlds = []
        self.predictor = {}

    def save(self):
        with open('agent_save.pickle', 'w') as f:
            pickle.dump([self.actions, self.worlds], f)
    @classmethod
    def load(cls):
        with open('agent_save.pickle', 'w+') as f:
            self.actions, self.worlds = pickle.load(f)


    def next(self, action):
        """The action and the world that it caused."""
        self.actions.append(action)
        self.worlds.append(self.cur())

    def cur(self):
        return [each() for each in self.inputs]

    def action_count(self, action):
        freq = [(each[0], len(list(each[1]))) for each in itertools.groupby(self.actions)]
        action_count = {}
        for key, val in freq:
            action_count[key] = val
        return action_count[action]

    def make_predictor(self):
        predictor = {}
        for world, action in zip(self.worlds, self.actions):
            predictor[action] = predictor.get(action, {})
            for id, inpt in enumerate(world):
                predictor[action][id] = predictor[action].get(id, {})
                predictor[action][id][inpt] = predictor[action][id].get(inpt, 0) + 1
        print predictor
        self.predictor = predictor

    def rf(self, x,y):
        return x*1.0/self.action_count(action)*y*1.0/self.action_count(action)

    def predict(self):
        scores = {}
        current_world = self.cur()
        for action, inputs in self.predictor.items():
            occurances = [self.predictor[action][model].get(cur, 0) for cur, model in zip(current_world, inputs)]
            print action, occurances, sum(occurances)
            prob = 1.0
            for oc in occurances:
                sgp = oc/self.action_count(action)
                if sgp == 0.0:
                    sgp += .02
                print prob, "x", sgp
                prob *= oc/self.action_count(action)
            prob *= self.action_count(action)/len(self.actions) # /self.probability_of_all_senses(current_world)
            scores[action] = prob

        print "scores are", scores
        r = random.uniform(0,1)
        for action, score in scores.items():
            r -= score
            if r < 0:
                return action
        return max(scores.iterkeys(), key=lambda k: scores[k])[0]
