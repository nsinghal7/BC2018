import battlecode as bc
import random
import sys
import traceback
import time
import math
import phase0
import phase1
from utilities import Point
from utilities import KarbCluster
from utilities import Container
from utilities import UnitInfo

import os


def main():
    self = Container()
    UnitInfo.setup()
    print(os.getcwd())

    print("pystarting")

    # A GameController is the main type that you talk to the game with.
    # Its constructor will connect to a running game.
    self.gc = bc.GameController()

    print("pystarted")

    # It's a good idea to try to keep your bots deterministic, to make debugging easier.
    # determinism isn't required, but it means that the same things will happen in every thing you run,
    # aside from turns taking slightly different amounts of time due to noise.
    random.seed(6137)
    
    # Ex: self.dir_to_dxdy[bc.Direction.Southeast.value] => Point(-1, 1)
    self.dir_to_dxdy = [Point(1, 0), Point(1, 1), Point(0, 1), Point(-1, 1), Point(-1, 0), Point(-1, -1), Point(0, -1), Point(1, -1), Point(0, 0)]
    # Ex: self.dxdy_to_dir[-1][1] => bc.Direction.Southeast
    self.dxdy_to_dir = [[bc.Direction.Center, bc.Direction.East, bc.Direction.West],
                        [bc.Direction.North, bc.Direction.Northeast, bc.Direction.Northwest],
                        [bc.Direction.South, bc.Direction.Southeast, bc.Direction.Southwest]]
    self.directions = self.dir_to_dxdy[:-1]
    
    self.planet = self.gc.planet()
    self.team = self.gc.team()
    self.asteroids = self.gc.asteroid_pattern()
    self.orbit = self.gc.orbit_pattern()
    
    self.start_map = phase0.generate_start_map(self)
    
    if self.planet == bc.Planet.Earth:
        main_earth(self)
    else:
        main_mars(self)

def main_earth(self):
    # let's start off with some research!
    # we can queue as much as we want.
    self.gc.queue_research(bc.UnitType.Worker) #more harvest 25
    self.gc.queue_research(bc.UnitType.Worker) #more build 100
    self.gc.queue_research(bc.UnitType.Mage) #more damage 125

    self.karb_clusters, self.neighbors = phase0.earth_karbonite_search(self)
    phase1.replicate_workers_phase(self)
    #TODO
    

if __name__ == '__main__':
    main()