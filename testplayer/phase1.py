from utilities import try_nearby_directions
from utilities import Path
from utilities import Point
from utilities import factory_loc_check_update
from utilities import begin_round
from utilities import end_round
import battlecode as bc
import random

PHASE1_WORKERS_WANTED = 10
ABILITY_COOLDOWN_LIMIT = 10
FACTORY_BUILD_COST = 100
KARBONITE_FOR_REPLICATE = 30

def replicate_workers_phase(state):
    units = state.gc.units()
    extras = []
    replicate_id = units[0].id
    cluster_index = 0
    score = -1
    for unit in units:
        for index in range(len(state.karb_clusters)):
            ns = cluster_worker_score(unit.location.map_location(), state.karb_clusters[index])
            if ns > score:
                replicate_id, cluster_index, score = unit.id, index, ns
    for unit in units:
        unit.info().is_B_group = (unit.id == replicate_id)

    while len(units) + len(extras) < PHASE1_WORKERS_WANTED:

        end_round(state)
        units = state.gc.units()
        extas = []
                

def is_clear(state, ml):
    for i in range(9):
        direction = bc.Direction(i)
        new = ml.add(direction)
        if not state.gc.can_sense_location(new):
            return False
        if not state.gc.planet_map.is_passable_terrain_at(new):
            return False
        unit = state.gc.sense_unit_at_location(new)
        if unit is not None and unit.unit_type in [bc.UnitType.Factory, bc.UnitType.Rocket]:
            return False
    return True

def try_harvest(state, unit, goal):
    for direction in try_nearby_directions(goal):
        if state.gc.can_harvest(unit.id, direction):
            state.gc.harvest(unit.id, direction)
            return True
    return False

def cluster_worker_score(ml, cluster):
    if cluster[ml.y][ml.x] is None:
        return -1
    dist = cluster[ml.y][ml.x][1]
    val = cluster.karb
    if dist == 0:
        return 2 * val
    return val / dist ** 2