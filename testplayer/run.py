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
    self.planet_map = self.gc.starting_map(self.planet)
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
    self.gc.queue_research(bc.UnitType.Rocket)
    self.gc.queue_research(bc.UnitType.Worker) #more build 100
    self.gc.queue_research(bc.UnitType.Mage) #more damage 125

    # self.karb_clusters is a list of KarbClusters
    # self.neighbors[row][col] is a list of Paths to nearby karbonite within a cluster
    # self.cmap[row][col] is a cluster id, 0 <= id < len(self.karb_clusters), or -1 if (row, col) is not part of a cluster
    self.destinations = []
    self.symmetry = phase0.get_symmetry(self)
    phase0.add_og_poi(self)
    self.karb_clusters, self.neighbors, self.cmap = phase0.earth_karbonite_search(self)
    self.destinations += self.karb_clusters
    self.mars_map = self.gc.starting_map(bc.Planet.Mars)
    try:
        b_info = phase1.replicate_workers_phase(self)
    except Exception as e:
        raise(e)
    while True:
        units, factories = [], []
        for unit in self.gc.my_units:
            if unit.unit_type == bc.UnitType.Factory:
                factories.append(unit)
            elif unit.unit_type != bc.UnitType.Rocket:
                units.append(unit)
            else:
                nearby = self.gc.sense_nearby_units(unit.location.map_location(), 2)
                for other in nearby:
                    if self.gc.can_load(unit.id, other.id):
                        self.gc.load(unit.id, other.id)
                if unit.structure_garrison() == unit.structure_max_capacity():
                    x, y = (int)(random.random() * self.mars_map.width), (int)(random.random() * self.mars_map.height)
                    loc = bc.MapLocation(bc.Planet.Mars, x, y)
                    while not self.mars_map.is_passable_terrain_at(loc):
                        x, y = (int)(random.random() * self.mars_map.width), (int)(random.random() * self.mars_map.height)
                        loc = bc.MapLocation(bc.Planet.Mars, x, y)
                    og = unit.location.map_location()
                    _y, _x = og.y, og.x
                    for i in range(len(self.destinations)):
                        d = self.destinations[i]
                        if d.rocket and d[_y][_x][1] == 0:
                            self.destinations = self.destinations[:i] + self.destinations[i + 1:]
                            break
                    self.gc.launch_rocket(unit.id, loc)
        r = random.random()
        phase1.process_units(self, units, factories, b_info, lambda: bc.UnitType.Ranger if r > .4 else bc.UnitType.Mage)
        self.gc.next_turn()
    #TODO

def main_mars(self):
    while True:
        self.gc.next_turn()
    pass
    

if __name__ == '__main__':
    main()