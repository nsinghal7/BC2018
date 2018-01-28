from utilities import try_nearby_directions
from utilities import Path
from utilities import Point
from utilities import factory_loc_check_update
from utilities import harvest
from utilities import UnitQueue
from utilities import end_round
from utilities import Container
from utilities import process_worker
import battlecode as bc
import random
import sys

PHASE1_WORKERS_WANTED = 7
HEAT_LIMIT = 10
FACTORY_BUILD_COST = 200
KARBONITE_FOR_REPLICATE = 60

def replicate_workers_phase(state):
    units = state.gc.my_units()
    extras = []
    replicate_id = units[0].id
    cluster_index = 0
    cluster_reset = False
    score = -1
    gc = state.gc
    for unit in units:
        for index in range(len(state.karb_clusters)):
            ns = _cluster_worker_score(unit.location.map_location(), state.karb_clusters[index])
            if ns > score:
                replicate_id, cluster_index, score = unit.id, index, ns
    for row in state.cmap[::-1]:
        for val in row:
            print(". " if val == -1 else (str(val) + " "), end=" ")
        print()
    for unit in units:
        unit.info().is_B_group = (unit.id == replicate_id)

    while len(units) < PHASE1_WORKERS_WANTED:
        index = 0
        while index < len(units) + len(extras):
            lu = len(units)
            if index < lu:
                unit = units[index]
            else:
                unit = extras[index - lu]
            ui = unit.info()
            ml = unit.location.map_location()

            if ui.is_B_group:
                goal_pt, dist = state.karb_clusters[cluster_index][ml.y][ml.x]
                if (not cluster_reset and ui.reached_cluster) or goal_pt.x == goal_pt.y == 0:
                    # reached cluster
                    was_reset = cluster_reset
                    cluster_reset = False
                    ui.reached_cluster = True
                    process_worker(state, unit)
                    unit = gc.unit(unit.id)
                    if ui.mode == 'random' and not was_reset:
                        cluster_reset = True
                        score = -1
                        for i in range(len(state.karb_clusters)):
                            ns = _cluster_worker_score(ml, state.karb_clusters[i])
                            if ns > score:
                                score, cluster_index = ns, i
                        print("reset")
                        continue
                    else:
                        #panic
                        print("panic")
                        cluster_index = (cluster_index + 1) % len(state.karb_clusters)
                        cluster_reset = True
                else:
                    # en route
                    goal = None
                    if gc.is_move_ready(unit.id):
                        for direction in try_nearby_directions(goal_pt.to_Direction()):
                            if gc.can_move(unit.id, direction):
                                gc.move_robot(unit.id, direction)
                                unit = gc.unit(unit.id)
                                goal = direction.opposite()
                                break
                    goal = goal or (-goal_pt).to_Direction()
                    try_harvest(state, unit, goal)
                if len(units) + len(extras) < PHASE1_WORKERS_WANTED and gc.karbonite() > KARBONITE_FOR_REPLICATE and unit.ability_heat() < HEAT_LIMIT:
                    goal = bc.Direction.North if ui.reached_cluster else goal_pt.to_Direction() # make goal in cluster better
                    print("im trying to replicate")
                    for direction in try_nearby_directions(goal):
                        ml = unit.location.map_location()
                        nloc = ml.add(direction)
                        if  gc.can_replicate(unit.id, direction):
                            c = len(units)
                            gc.replicate(unit.id, direction)
                            new = gc.sense_unit_at_location(nloc)
                            new.info().is_B_group = True
                            extras.append(new)
                            break
            else:
                process_worker(state, unit)
            index+=1
        end_round(state)
        units = state.gc.my_units()
        extras = []
    
    leader = True
    gi = Container()
    for unit in units:
        ui = unit.info()
        if ui.is_B_group:
            ui.worker_group = 0
            ui.worker_is_leader = leader
            leader = False
            ui.worker_group_info = gi
    gi.target = cluster_index
    fi.factory_loc = None

    while True:
        allUnits = gc.my_units()
        extras = []
        factories = []
        units = []
        for unit in allUnits:
            if unit.unit_type in [bc.UnitType.Factory or bc.UnitType.Rocket]:
                factories.append(unit)
            else:
                units.append(unit)

        worker_factory_logic(state, units, extras, factories)

        end_round(state)



def worker_factory_logic(state, units, extras, factories):
    """
    Controls workers in a general situation with the goal of building factories.
    Returns True if built a factory, else False. ASSUMES UnitQueue has been initialized for all
    units currently in units or extras. ASSUMES units is a list of only robots
    """
    
                

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
        if harvest(state, unit, direction):
            return True
    return False

def _cluster_worker_score(ml, cluster):
    if cluster[ml.y][ml.x] is None:
        return -1
    dist = cluster[ml.y][ml.x][1]
    val = cluster.karb
    if dist == 0:
        return 2 * val
    return val / dist ** 2
