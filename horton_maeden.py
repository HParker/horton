# This is a horton agent designed to solve puzzles in the Maeden environment.

import horton
import socket

mouse = who() # mind

# boiler plate

@request(mouse, {'start': True})
def live(effectors):
    # body
    mouse.s = socket.socket(socekt.AF_INET, socket.SOCK_STREAM).connect(('localhost', 7237))
    mouse.s.send("base\n")

@request(mouse {'end': True})
def die(effectors):
    mouse.s = s.close()
    effector['quit']()


@apperseption(mouse)
def parse_senses():


@sense(mouse)
def smell():
