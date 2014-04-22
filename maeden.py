from tantor import Tantor
from predictors import Bayes, Lazy
import re
import socket
import time

class Controller:
    def __init__(self):
        self.world = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost',7237))
        self.sock.send("base\n")
        self.process_input()

    def process_input(self):
        time.sleep(.5)
        input_string = self.sock.recv(1024)
        lines = input_string.split('\n')
        if len(lines) == 2:
            self.world['id'] = lines[0]
            return
            self.do('u') # use is sure to not change the environment
            # just used here to avoid [None, N, N] senses.
        if lines[0] == '8':
            self.world['smell'] = lines[1]
            self.world['inv'] = lines[2]
            vision = self.process_vision(lines[3])
            self.world['vis1'] = vision[0]
            self.world['vis2'] = vision[1]
            self.world['vis3'] = vision[2]
            self.world['vis4'] = vision[3]
            self.world['ground'] = lines[4]
            self.world['messages'] = lines[5]
            self.world['energy'] = lines[6]
            self.world['result'] = lines[7]
            self.world['time'] = lines[8]
        else:
            return 'done'

    def get(self, sense):
        return self.world.get(sense, None)

    def smell(self):
        return self.get('smell')
    def inventory(self):
        return self.get('inv')
    def ground(self):
        return self.get('ground')
    def result(self):
        return self.get('result')
    def vis1(self):
        return self.get('vis1')
    def vis2(self):
        return self.get('vis2')
    def vis3(self):
        return self.get('vis3')
    def vis4(self):
        return self.get('vis4')

    def process_vision(self, string):
        # (((|((|) (|))((|)))
        p = re.compile("\\(\\(\\(|\\)\\s\\(|\\)\\)\\(\\(|\\)\\)\\)")
        vis = p.split(string)
        return [vis[4], vis[8], vis[10], vis[13]]

    def do(self, action):
        if action in ['f', 'b', 'l', 'r', 'g', 'u', 'd']:
            print "doing", action
            self.sock.send(action+"\n")
            self.process_input()
        else:
            print "Error:", action, "not a proper action."

    def train(self, t):
        while True:
            move = raw_input("train =>")
            if move == "quit":
                break
            t.rec(move)
            self.do(move)

    def run(self, t):
        n = 20
        i = 0
        while True:
            move = t.predict()
            self.do(move)
            i += 1
            if move == 'u' or i == n:
                cont = raw_input("continue? [y/N] ->")
                if cont == 'y':
                    n += 10
                else:
                    return

if __name__ == "__main__":
    while True:
        resp = raw_input("Tantor ->")
        if resp == 'train':
            c = Controller()
            t = Tantor([c.smell,   c.inventory,
                        c.ground,  c.result,
                        c.vis1,    c.vis2,
                        c.vis3,    c.vis4])
            c.train(t)
        elif resp == 'run':
            c = Controller()
            t.infns = [c.smell,   c.inventory,
                        c.ground,  c.result,
                        c.vis1,    c.vis2,
                        c.vis3,    c.vis4]
            c.run(t)
        elif resp == 'save':
            fn = raw_input("filename:")
            t.save(fn+".txt")
        elif resp == 'load':
            t = Tantor()
            fn = raw_input("filename:")
            t.load(fn+".txt")
        elif resp == 'learn':
            t.learn(Bayes)
        elif resp == 'exit':
            exit()
        else:
            print "Try again."
