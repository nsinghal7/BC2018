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
    
    # For the purposes of this program, (0, 0) is the UPPERLEFT corner and Point(y, x) <=> [y][x] <=> bc.MapLocation(self.planet, x, y)
    
    self.directions = [Point(1, 0), Point(1, 1), Point(0, 1), Point(-1, 1), Point(-1, 0), Point(-1, -1), Point(0, -1), Point(1, -1)]
    
    self.planet = self.gc.planet()
    self.team = self.gc.team()
    self.asteroids = self.gc.asteroid_pattern()
    self.orbit = self.gc.orbit_pattern()
    
    # self.kmap[row][col] is an amount of karbonite >= 0 or -1 if impassable
    self.kmap = phase0.generate_kmap(self)
    
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

    # self.karb_clusters is a list of KarbClusters
    # self.neighbors[row][col] is a list of Paths to nearby karbonite within a cluster
    # self.cmap[row][col] is a cluster id, 0 <= id < len(self.karb_clusters), or -1 if (row, col) is not part of a cluster
    self.karb_clusters, self.neighbors, self.cmap = phase0.earth_karbonite_search(self)
    self.destinations = self.karb_clusters[:] # add POIs
    phase1.replicate_workers_phase(self)
    #TODO
    

if __name__ == '__main__':
    main()