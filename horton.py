class who(object):
    """ represents the agency of a program in horton.
    i.e. Posessor of beliefs, desires and intentions.
    listener of assertions and requests"""
    def __init__(self, assertions = {}, senses = {}, requests = {}, effectors = {}):
        """ create a set of hashtables to store the knowledge of the agent """
        self.assertions = assertions
        self.senses = senses
        self.requests = requests
        self.effectors = effectors
        # add a quit effector
        self.effectors['quit'] = exit
        self.sense_cache = {}
        self.sensemap = {}

    def __call__(self): # not sure what this is for anymore
        return self

    def cache(self):
        """ get the current state of the sense data.
        also return if the sense data is new or not, which helps avoid checking repeated values."""
        prev = self.sense_cache
        for (name, function) in self.senses.iteritems():
            val = function()
            if val == prev.get(name, None):
                self.sense_cache[name] = (False, val)
            else:
                self.sense_cache[name] = (True, val)


    def index_senses(self):
        """ create a reverse index type table for senses -> beliefs.
        this makes it so when a sense changes, we know which beliefs might have changed as well."""
        for (key, val) in self.assertions.iteritems():
            for sense in val["senses"]:
                req = self.sensemap.get(sense, [])
                req.append(key)
                self.sensemap[sense] = req
                print self.sensemap[sense]

        print "sense map---------------"
        print self.sensemap

    def trigger(self, asrt):
        """ just run the belief. """
        return self.assertions[asrt]["action"](self.sense_cache)


    def start(self):
        """ a loop over that caches sense data, keeps an updated set of beliefs based on that
        and uses the state of those beliefs to trigger requests."""
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
                print "beliefs========"
                print cur_beliefs
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



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATORS
#
# These provide a means of giving functions to the agent.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class assertion(object):
    """ decorator to assign functions to a who instance"""
    def __init__(self, who, senses=[]):
        self.assertions = who.assertions
        self.senses = senses # eventually, can limit this to necisary senses

    def __call__(self, f):
        self.assertions[f.__name__] = {"action":f, "senses":self.senses}


class request(object):
    """ decorator that adds a request to a who instance """
    def __init__(self, who, assertions={}):
        self.requests = who.requests
        self.assertions = assertions
    def __call__(self, f):
        self.requests[f.__name__] = {"action":f, "assertions":self.assertions}


class sense(object):
    """ decorator for adding senses to to an agent """
    def __init__(self, who):
        self.senses = who.senses
    def __call__(self, f):
        self.senses[f.__name__] = f

class effect(object):
    """ decorator for effecting the environment """
    def __init__(self, who):
        self.effectors = who.effectors
    def __call__(self, f):
        self.effectors[f.__name__] = f


if __name__ == "__main__":
    """ example attemting to show how a simple 1D agent
    might find its way from one point to another. """
    agent = who() # make an agent

    @sense(agent)
    def food_location():
        f = open("state.txt", "r")
        s = f.read().split()
        print "food-----"
        print s[0]
        return s.pop(0)

    @sense(agent)
    def self_location():
        f = open("state.txt", "r")
        s = f.read().split()
        print "me-------"
        print s[len(s)-1]
        return s.pop()


    @effect(agent)
    def move_forward():
        with open("state.txt", "r+") as f:
            s = f.read().split()
            f.write(" "+str(int(s.pop())+1))

    @effect(agent)
    def move_backward():
        with open("state.txt", "r+") as f:
            s = f.read().split()
            f.write(" "+str(int(s.pop())-1))

    @assertion(agent, ["food_location", "self_location"]) # add a belief to the agent
    def food_forward(senses): # uses a cash of the sense data
        print "comparing food location to self location"
        print "food:", senses["food_location"]
        print "me:", senses["self_location"]
        return senses["food_location"] > senses["self_location"]


    @assertion(agent, ["food_location", "self_location"])
    def at_food(senses):
        return senses["food_location"] == senses["self_location"]

    @request(agent, {'food_forward': True})
    def move_forward_to_food(effectors):
        effectors['move_forward']()
        print "moving forward towards the food"

    @request(agent, {'food_forward': False})
    def move_backward_to_food(effectors):
        effectors['move_backward']()
        print "moving backwards towards the food"

    @request(agent, {'at_food': True})
    def eat(effectors):
        effectors['quit']()



    print "senses--------------"
    print agent.senses
    print "effectors--------------"
    print agent.effectors
    print "assertions--------------"
    print agent.assertions
    print "requests--------------"
    print agent.requests

    agent.start()
