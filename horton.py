class Memorable():
    """
    internal type for horton that stores values of senses and beliefs.
    This type allows for direct reforence to the past though a set of methods.
    """
    def __init__(self, val):
        self.vals = [val]
    def __cmp__(self, other):
        if isInstance(other, Memorable):
            return cmp(self.vals[-1], other.vals[-1])
        else:
            return cmp(self.vals[-1], other)
    def __getitem__(self, key):
        return self.vals[key]
    def __setitem__(self, key, value):
        self.vals[key] = value
    def __iter__(self):
        return iter(self.vals)

    def has_been(self, comparator):
        return comparator in self.vals
    def was(self, comparator):
        return comparator in self.vals[:-1]
    def is(self, comparator):
        if isInstance(other, Memorable):
            return self.vals[-1] == other
        else:
            return self.vals[-1] == other



class Agent(object):
    """
    represents the agency of a program in horton.
    i.e. Posessor of beliefs, desires and intentions.
    listener of assertions and requests.
    """
    def __init__(self):
        """ create a set of hashtables to store the knowledge of the agent """
        self.assertions = {}
        self.requests = {}
        self.senses = {}
        self.effectors = {}
        self.effectors['quit'] = exit
        self.sense_cache = {}
        self.sensemap = {}
        self.pre = []

    def cache(self):
        """
        get the current state of the sense data.
        also return if the sense data is new or not,
        which avoids checking repeated values.
        """
        pre = {}
        for p in self.pre:
            pre = dict(list(p().items()) + list(pre))

        prev = self.sense_cache
        for name, func in self.senses.iteritems():
            val = func(pre)
            if val == prev.get(func.__name__, None):
                self.sense_cache[name] = (False, val)
            else:
                self.sense_cache[name] = (True, val)

    def index_senses(self):
        """
        create a reverse index type table for senses -> beliefs.
        this makes it so when a sense changes, we know which beliefs might have changed as well.
        """
        for (key, val) in self.assertions.iteritems():
            for sense in val["senses"]:
                req = self.sensemap.get(sense, [])
                req.append(key)
                self.sensemap[sense] = req

    def trigger(self, asrt):
        """ just run the belief. with its senses """
        return self.assertions[asrt]["action"](self.sense_cache)


    def start(self):
        """
        a loop over that caches sense data, keeps an updated set of beliefs based on that
        and uses the state of those beliefs to trigger requests.
        """
        # cache senses, recheck
        # if a value chages check the beliefs that rely on it.
        self.index_senses()
        cur_beliefs = {}
        while True:
            self.cache()
            effected_assertions = set()
            for (sense_name, (is_new, val)) in self.sense_cache.iteritems():
                if is_new:
                    effected_assertions.update(self.sensemap[sense_name])
            for asrt in effected_assertions:
                cur_beliefs[asrt] = self.trigger(asrt)
            # TODO: refactor... not clear code
            for request, request_val in self.requests.iteritems(): # check requests
                is_satisfied = True # Assume true until proved otherwise
                for assertion, assertion_val in request_val['assertions'].iteritems(): # check that request's assertions
                    if assertion in cur_beliefs and assertion_val == cur_beliefs[assertion]:
                        pass
                    else:
                        is_satisfied = False
                if is_satisfied == True: # it this request's beliefs is currently believed and their value is the same
                    self.requests[request]['action'](self.effectors) # do it.



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATORS                                                 |
# -------------------                                        |
# These provide a means of giving functions to the agent.    |
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# TODO: add reference to the past.


class assertion(object):
    """ decorator to assign functions to a agent instance"""
    def __init__(self, agent, senses=[]):
        self.assertions = agent.assertions
        self.senses = senses
    def __call__(self, f):
        self.assertions[f.__name__] = {"action":f, "senses":self.senses}


class request(object):
    """ decorator that adds a request to a agent instance """
    def __init__(self, agent, assertions={}):
        self.requests = agent.requests
        self.assertions = assertions
    def __call__(self, f):
        self.requests[f.__name__] = {"action":f, "assertions":self.assertions}


class before(object):
    """
    decorator for minipulating information about the world before higher senses process them.
    Useful for when you need to grab multiple bits of information about the world at once.
    """
    def __init__(self, agent):
        # allows the program to perform a list of functions before senses, beliefs, requests, or effectors happen.
        self.pre = agent.pre
    def __call__(self, f):
        self.pre.append(f)

# TODO: allow to set pre/before things to do for this sense.
class sense(object):
    """ decorator for adding senses to an agent """
    def __init__(self, agent, pre="all"):
        self.pre = pre
        self.senses = agent.senses
    def __call__(self, f):
        self.senses[f.__name__] = f

class effect(object):
    """ decorator for effecting the environment """
    def __init__(self, agent):
        self.effectors = agent.effectors
    def __call__(self, f):
        self.effectors[f.__name__] = f


if __name__ == "__main__":
    """
    example attemting to show how a simple 1D agent
    might find its way from one point to another.
    """
    onede = Agent() # make an agent

    @before(onede)
    def establish_locations():
        with open("state.txt", "r") as f:
            s = f.read().split()
            return {'me': s.pop(), 'food': s.pop(0)}

    @sense(onede)
    def food_location(pre):
        return pre['food']

    @sense(onede)
    def self_location(pre):
        return pre['me']

    @effect(onede)
    def move_forward():
        with open("state.txt", "r+") as f:
            s = f.read().split()
            f.write(" "+str(int(s.pop())+1))

    @effect(onede)
    def move_backward():
        with open("state.txt", "r+") as f:
            s = f.read().split()
            f.write(" "+str(int(s.pop())-1))

    @assertion(onede, ["food_location", "self_location"]) # add a belief to the agent
    def food_forward(senses): # uses a cash of the sense data
        return senses["food_location"] > senses["self_location"]


    @assertion(onede, ["food_location", "self_location"])
    def at_food(senses):
        return senses["food_location"] == senses["self_location"]

    @request(onede, {'food_forward': True})
    def move_forward_to_food(effectors):
        effectors['move_forward']()
        print "moving forward towards the food"

    @request(onede, {'food_forward': False, 'at_food': False})
    def move_backward_to_food(effectors):
        effectors['move_backward']()
        print "moving backwards towards the food"

    @request(onede, {'at_food': True})
    def eat(effectors):
        effectors['quit']()

    print "pre-------------------"
    print onede.pre
    print "senses----------------"
    print onede.senses
    print "effectors-------------"
    print onede.effectors
    print "assertions------------"
    print onede.assertions
    print "requests--------------"
    print onede.requests

    onede.start()
