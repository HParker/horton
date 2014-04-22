from __future__ import division
import itertools
import operator
import code
import random
import math

class GenericPredictor: # general interface
    def __init__(self, data):
        self.model = self.build(data)

    def build(self, data):
        pass # will override

    def predict(self, world):
        pass


class Lazy(GenericPredictor):
    def build(self, data):
        for world in data.worlds:
            print world.action
            print world.data
        return data # put in self.model

    def predict(self, world):
        # find the world most symilar and do whatever was done then.
        best = self.model.worlds[-1]
        for s in self.model.worlds:
            if len(best.sim(world)) < len(s.sim(world)):
                best = s
        return best.action # this is done by the agent

class Bayes(GenericPredictor):
    def build(self, data):
        model = {}
        # count senses given action
        for world in data.worlds:
            model[world.action] = model.get(world.action, {})
            for id, sense in enumerate(world.data):
                model[world.action][id] = model[world.action].get(id, {})
                model[world.action][id][sense] = model[world.action][id].get(sense, 0) + 1

        # count actions in whole experience
        self.action_count = {}
        freq = [(each[0], len(list(each[1]))) for each in itertools.groupby([world.action for world in data.worlds])]
#        for world in data.worlds:
#            self.action_count[world.action] = self.action_count.get(world.action, 0) + 1
        self.worlds = data.worlds
        for key, val in freq:
            self.action_count[key] = val
        print model
        return model

    def prob_select(self, scores):
        max = 0.0
        for action, prob in scores.items():
            max += prob
        r = random.uniform(0, max)
        s = 0
        for action, prob in scores.items():
            s += prob
            if s >= r:
                return action
        return max(scores.iterkeys(), key=lambda k: scores[k])[0]

    def predict(self, current_world):
        scores = {}
        for action, inputs in self.model.items():
            occurances = []
            for cur, model in zip(current_world.data, inputs):
                occurances.append(self.model[action][model].get(cur, 0.0))
            print action, occurances, sum(occurances)
            prob = 1.0
            for oc in occurances:
                prob *= oc/self.action_count[action]
            prob *= self.action_count[action]/len(self.worlds)
            if prob == 0.0:
                prob = 0.001
            scores[action] = prob
        print "scores:", scores
        # return max(scores.iterkeys(), key=lambda k: scores[k])[0]
        return self.prob_select(scores)
