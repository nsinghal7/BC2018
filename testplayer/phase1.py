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
    factory_path = None
    fp_start = None
    factory_loc = None
    stuck = False
    score = -1
    for unit in units:
        for index in range(len(state.karb_clusters)):
            ns = cluster_worker_score(unit.location.map_location(), state.karb_clusters[index])
            if ns > score:
                replicate_id, cluster_index, score = unit.id, index, ns
    for unit in units:
        unit.info().is_B_group = (unit.id == replicate_id)
        unit.info().prevdir = bc.Direction.North

    while len(units) + len(extras) < PHASE1_WORKERS_WANTED:
        index = 0
        begin_round(state)
        while index < len(units) + len(extras):
            print("next unit")
            if index < len(units):
                unit = units[index]
            else:
                unit = extras[index - len(units)]
            ml = unit.location.map_location()
            if unit.info().is_B_group:
                path = unit.info().cluster_path
                goal = state.karb_clusters[cluster_index][ml.y][ml.x][0]
                if path is None and (goal.x != 0 or goal.y != 0):
                    # not there yet
                    print("im not at the cluster")
                    if state.gc.is_move_ready(unit.id):
                        for direction in try_nearby_directions(goal.to_Direction()):
                            if state.gc.can_move(unit.id, direction):
                                state.gc.move_robot(unit.id, direction)
                                unit.info().prevdir = direction
                                break
                    try_harvest(state, unit, (-goal).to_Direction())
                elif path is None:
                    # is there, but hasn't chosen path yet
                    neighbors = state.neighbors[ml.y][ml.x]
                    if factory_loc is None:
                        print("im first at the cluster")
                        # is the first one to reach the cluster, should set factory location
                        q = [Path(Point(ml.y, ml.x))]
                        index = 0
                        while index < len(q):
                            current = q[index]
                            index += 1
                            if factory_loc_check_update(state, bc.MapLocation(state.planet, current.dest.x, current.dest.y)):
                                # factory should be here, maps already updated
                                factory_loc = current.dest.y, current.dest.x
                                unit.info().cluster_path = current.steps.reverse()
                                factory_path = current.steps.reverse()
                                fp_start = ml
                                unit.info().cluster_dest_factory = True
                                break
                            for dy in range(-1, 2):
                                y = current.dest.y + dy
                                if not (0 <= y < len(state.kmap)):
                                    continue
                                for dx in range(-1, 2):
                                    x = current.dest.x + dx
                                    if 0 <= x < len(state.kmap[0]):
                                        if state.kmap[y][x] != -1:
                                            q.append(current + Point(dy, dx))
                        if factory_loc is None:
                            raise Exception("There is absolutely nowhere to put a factory that doesn't ruin things")
                    elif len(neighbors) == 0:
                        print("i have no friends")
                        unit.info().cluster_path = factory_path #the only place you could be is the only square in the cluster
                        unit.info().cluster_dest_factory = True
                    else:
                        print("i do have friends")
                        unit.info().cluster_path = random.choice(neighbors).steps.reverse()
                        unit.info().cluster_dest_factory = False

                path = unit.info().cluster_path
                if path is not None and state.gc.is_move_ready(unit.id) and unit.info().prevdir is not None:
                    print("im on the target!")
                    if len(path) == 0:
                        # move out of the way! go past the square in same direction as before hopefully
                        o = bc.Direction.North
                        moved = False
                        for direction in try_nearby_directions(unit.info().prevdir):
                            if state.gc.can_move(unit.id, direction):
                                state.gc.move_robot(unit.id, direction)
                                unit.info().prevdir = None
                                o = direction.opposite()
                                unit.info().cluster_path = Point(o)
                                moved = True
                                break
                        if not moved and unit.info().cluster_dest_factory:
                            stuck = True
                        #harvest goal location or nearby
                        try_harvest(state, unit, o)
                    elif stuck:
                        print("halp we're stuck")
                        unit.info().is_B_group = False
                    else:
                        print("im following a path")
                        goal = path.pop()
                        for direction in try_nearby_directions(goal.to_Direction()):
                            if state.gc.can_move(unit.id, direction):
                                state.gc.move_robot(unit.id, direction)
                                unit.info().prevdir = direction
                                if direction != goal:
                                    path.append(goal)
                                    path.append(-Point(direction))
                                break
                        try_harvest(state, unit, direction.opposite())
                elif path is not None:
                    print("already done")
                    # harvest in factory after passing it
                    try_harvest(state, unit, path[-1].to_Direction())

                if unit.ability_heat() < ABILITY_COOLDOWN_LIMIT and len(units) < PHASE1_WORKERS_WANTED and state.gc.karbonite() > KARBONITE_FOR_REPLICATE:
                    print("making babies")
                    if path is None or len(path) == 0:
                        goal = Point(unit.info().prevdir or bc.Direction.North)
                    else:
                        goal = path[-1]
                    for direction in try_nearby_directions(goal.to_Direction()):
                        if state.gc.can_replicate(unit.id, direction):
                            state.gc.replicate(unit.id, direction)
                            new = state.gc.sense_unit_at_location(ml.add(direction))
                            ui = new.info()
                            ui.is_B_group = True
                            ui.prevdir = direction
                            ui.cluster_path = path[:-1] if path else None
                            ui.cluster_dest_factory = unit.info().cluster_dest_factory
                            extras.append(new)
                            break
            if not unit.info().is_B_group:#not b
                # not B group
                print("i'm a loser")
                pass
            index += 1
        end_round(state)
        units = state.gc.units()
                
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