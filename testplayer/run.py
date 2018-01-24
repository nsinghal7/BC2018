import battlecode as bc
import random
import sys
import traceback
import time
import math
from phase1 import replicate_workers_phase
import utilities

import os


def main():
    self = main
    print(os.getcwd())

    print("pystarting")

    # A GameController is the main type that you talk to the game with.
    # Its constructor will connect to a running game.
    self.gc = bc.GameController()
    self.directions = list(bc.Direction)
    self.directionMap = [[bc.Direction.Northwest, bc.Direction.North, bc.Direction.Northeast],
                        [bc.Direction.West, bc.Direction.Center, bc.Direction.East],
                        [bc.Direction.Southwest, bc.Direction.South, bc.Direction.Southeast]]

    print("pystarted")

    # It's a good idea to try to keep your bots deterministic, to make debugging easier.
    # determinism isn't required, but it means that the same things will happen in every thing you run,
    # aside from turns taking slightly different amounts of time due to noise.
    random.seed(6137)

    # let's start off with some research!
    # we can queue as much as we want.
    self.gc.queue_research(bc.UnitType.Worker) #more harvest 25
    self.gc.queue_research(bc.UnitType.Worker) #more build 100
    self.gc.queue_research(bc.UnitType.Mage) #more damage 125


    self.planet = gc.planet()
    self.start_map = gc.starting_map(planet)
    self.team = gc.team()

    replicate_workers_phase(self)
    #TODO