from utilities import try_nearby_directions
from utilities import Path
from utilities import Point
from utilities import factory_loc_check_update
from utilities import harvest
from utilities import UnitQueue
from utilities import end_round
from utilities import Container
from utilities import process_worker
from utilities import process_attacker
from utilities import make_poi
from utilities import choose_attacking_units
import battlecode as bc
import random
import sys

PHASE1_WORKERS_WANTED = 5
MIN_WORKERS = 8
HEAT_LIMIT = 10
FACTORY_BUILD_COST = 200
ROCKET_BUILD_COST = 150
KARBONITE_FOR_REPLICATE = 60
MIN_FACTORIES = 6

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
    #TODO: FIGURE out how to decide if new unit is in B group
    gi = Container()
    gi.count = 0
    gi.prevcount = 0
    gi.ocount = 0
    gi.oprevcount = 0
    for unit in units:
        ui = unit.info()
        ui.arrived = False
        if ui.is_B_group:
            gi.count += 1
            gi.prevcount += 1
        else:
            gi.ocount += 1
            gi.oprevcount += 1
    gi.target = cluster_index
    gi.factory_loc = None
    stop = False
    print("starting phase1 part 2")
    while not stop:
        allUnits = gc.my_units()
        factories = []
        units = []
        for unit in allUnits:
            if unit.unit_type in [bc.UnitType.Factory or bc.UnitType.Rocket]:
                factories.append(unit)
            else:
                units.append(unit)
        stop = process_units(state, units, factories, gi, choose_attacking_units)

        end_round(state)
    return gi



def process_units(state, units, factories, b_info, create_type):
    """
    Controls workers in a general situation with the goal of building factories.
    Returns True if built a factory, else False. ASSUMES UnitQueue has been initialized for all
    units currently in units. ASSUMES units is a list of only robots
    """
    ans = False
    gc = state.gc
    b_info.prevcount = b_info.count
    b_info.oprevcount = b_info.ocount
    b_info.count = 0
    b_info.ocount = 0
    for factory in factories:
        if not factory.structure_is_built():
            continue
        sg = len(factory.structure_garrison())
        ml = factory.location.map_location()
        if sg > 0:
            for direction in try_nearby_directions(bc.Direction.North):
                if gc.can_unload(factory.id, direction):
                    gc.unload(factory.id, direction)
                    new = gc.sense_unit_at_location(ml.add(direction))
                    units.append(new)
                    if new.unit_type == bc.UnitType.Worker and  b_info.prevcount < MIN_WORKERS:
                        new.info().is_B_group = True
                    sg -= 1
                    if sg == 0:
                        break
        ct = create_type()
        if gc.can_produce_robot(factory.id, ct):
            gc.produce_robot(factory.id, ct)
    index = 0
    while index < len(units):
        moved = False
        unit = units[index]
        if unit.location.is_in_garrison():
            index += 1
            continue
        ml = unit.location.map_location()
        ui = unit.info()
        if unit.unit_type == bc.UnitType.Worker:
            print("control worker")
            if (b_info.prevcount < MIN_WORKERS or b_info.oprevcount < MIN_WORKERS) and unit.ability_heat() < HEAT_LIMIT and  gc.karbonite() > KARBONITE_FOR_REPLICATE:
                #panic and replicate
                print("REPLICATING: %d %d" % (b_info.prevcount, b_info.oprevcount))
                for direction in try_nearby_directions(bc.Direction.North):
                    if gc.can_replicate(unit.id, direction):
                        gc.replicate(unit.id, direction)
                        new = gc.sense_unit_at_location(ml.add(direction))
                        units.append(new)
                        if (ui.is_B_group and b_info.oprevcount >= MIN_WORKERS) or b_info.prevcount < 3:
                            new.info().is_B_group = True
                        elif (not ui.is_B_group and b_info.prevcount >= MIN_WORKERS) or b_info.oprevcount < 3:
                            new.info().is_B_group = False
                        else:
                            new.info().is_B_group = b_info.prevcount <= b_info.oprevcount
                        break
            #continue as normal, don't replicate
            if ui.is_B_group:
                b_info.count += 1
                built = False
                if b_info.factory_loc is None and len(factories) < MIN_FACTORIES and gc.karbonite() > FACTORY_BUILD_COST:
                    # try build factory 
                    for direction in try_nearby_directions(bc.Direction.North):
                        nloc = ml.add(direction)
                        if gc.can_blueprint(unit.id, bc.UnitType.Factory, direction) and factory_loc_check_update(state, nloc):
                            #must blueprint
                            gc.blueprint(unit.id, bc.UnitType.Factory, direction)
                            b_info.factory_loc = make_poi(state, Point(nloc.y, nloc.x), factory=True)
                            b_info.factory_id = gc.sense_unit_at_location(nloc).id
                            built = True
                            break
                elif b_info.factory_loc is None and gc.karbonite() > ROCKET_BUILD_COST:
                    # try build rocket
                    for direction in try_nearby_directions(bc.Direction.North):
                        nloc = ml.add(direction)
                        if gc.can_blueprint(unit.id, bc.UnitType.Rocket, direction):
                            gc.blueprint(unit.id, bc.UnitType.Rocket, direction)
                            b_info.factory_loc = make_poi(state, Point(nloc.y, nloc.x), factory=True)
                            b_info.factory_id = gc.sense_unit_at_location(nloc).id
                            built = True
                            break
                elif b_info.factory_loc is not None:
                    # should go to factory
                    if gc.is_move_ready(unit.id) and not moved:
                        try:
                            goal, dist = state.destinations[b_info.factory_loc][ml.y][ml.x]
                        except:
                            index += 1
                            continue
                        goal = goal.to_Direction()
                        if dist == 1:
                            lg = goal.rotate_left()
                            rg = goal.rotate_right()
                            if gc.can_move(unit.id, lg) and gc.is_move_ready(unit.id):
                                gc.move_robot(unit.id, lg)
                                moved = True
                            elif gc.can_move(unit.id, rg) and gc.is_move_ready(unit.id):
                                gc.move_robot(unit.id, rg)
                                moved = True
                            #else do nothing
                            if gc.can_build(unit.id, b_info.factory_id):
                                gc.build(unit.id, b_info.factory_id)
                                if gc.unit(b_info.factory_id).structure_is_built():
                                    ans = True
                                    fac = gc.unit(b_info.factory_id).unit_type == bc.UnitType.Factory
                                    if not fac:
                                        destmap = state.destinations[b_info.factory_loc]
                                        destmap.rocket = True
                                        destmap.factory = False
                                    b_info.factory_loc = None
                                    b_info.target -= 1
                                    b_info.factory_id = None

                            else:
                                print("should build but didn't")
                                print(index)

                        elif not moved and gc.is_move_ready(unit.id):
                            for direction in try_nearby_directions(goal):
                                if gc.can_move(unit.id, direction):
                                    gc.move_robot(unit.id, direction)
                                    moved = True
                                    break
                    try_harvest(state, unit, bc.Direction.North)
                if not built and b_info.factory_loc is None:
                    # go to cluster or switch B cluster
                    cluster = state.karb_clusters[b_info.target]
                    if cluster.karb > 0 and cluster[ml.y][ml.x] is not None:
                        goal, dist = cluster[ml.y][ml.x]
                        goal = goal.to_Direction()
                        if ui.arrived or goal == bc.Direction.Center:
                            ui.arrived = True
                            process_worker(state, gc.unit(unit.id))
                            moved = True
                        elif not moved and gc.is_move_ready(unit.id):
                            ui.arrived = False
                            unit = gc.unit(unit.id)
                            for direction in try_nearby_directions(goal):
                                if gc.can_move(unit.id, direction):
                                    gc.move_robot(unit.id, direction)
                                    moved = True
                                    break
                            try_harvest(state, unit, goal.opposite())
                    else:
                        # switch B cluster
                        prev = b_info.target
                        cid = 0
                        score = -1
                        for i in range(len(state.karb_clusters)):
                            s = _cluster_worker_score(ml, state.karb_clusters[i])
                            if s > score and i != prev:
                                cid, score = i, s
                        b_info.target = cid
                        if cluster[ml.y][ml.x] is None:
                            ui.is_B_group = False
                            index += 1
                            continue
                        goal, dist = cluster[ml.y][ml.x]
                        goal = goal.to_Direction()
                        if not moved and gc.is_move_ready(unit.id):
                            for direction in try_nearby_directions(goal):
                                if gc.can_move(unit.id, direction):
                                    gc.move_robot(unit.id, direction)
                                    moved = True
                                    break
                        try_harvest(state, unit, goal.opposite())


            if not ui.is_B_group:
                b_info.ocount += 1
                # should just harvest
                process_worker(state, unit)
        else:
            print("control attacker")
            process_attacker(state, unit)
        index += 1
    return ans



    
                

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
