import horton
import libardrone
from time import sleep


drone = who()
dronec = libardrone.ARDrone(True)
dronec.reset()

@sense(drone)
def flying():
    return dronec.last_command_is_hovering

@effect(drone)
def fly():
    dronec.takeoff()
    dronec.hover()


@effect(drone)
def land():
    dronc.land()

@assertion(drone, ['flying'])
def should_fly(sense):
    return !sense['flying']

@request(drone, {'should_fly': True})
def fly_a_little(effectors):
    effectors['fly']()
    sleep(5)

@request(drone, {'should_fly': False})
def land_now(effectors):
    effectors['land']()
