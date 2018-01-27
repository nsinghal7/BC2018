import utilities
import battlecode as bc

PHASE1_WORKERS_WANTED = 10
ABILITY_COOLDOWN_LIMIT = 10
FACTORY_BUILD_COST = 100

def replicate_workers_phase(state):
    units = state.gc.units()
    factory_loc = None #TODO
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

    begin_building = False
    blueprint_laid = False

    while True:
        index = 0
        while index < len(units):
            if unit.info().is_B_group:
                ml = unit.location.map_location()
                goal = state.karb_clusters[cluster_index][ml.y][ml.x]
                skip_exact = goal[1] == 1
                # move and determine direction to replicate
                if goal[0] == bc.Direction.Center: #shouldn't happen
                    for direction in try_nearby_directions(bc.Direction.North):
                        if gc.can_move(unit.id, direction):
                            gc.move_robot(unit.id, direction)
                            ml = ml.add(direction)
                            goal = direction.opposite(), 1
                            skip_exact = True
                            break
                    if goal == bc.Direction.Center:
                        goal = bc.Direction.North, 0
                        skip_exact = False
                else:
                    for direction in try_nearby_directions(goal[0], skip_exact):
                        if gc.can_move(unit.id, direction):
                            gc.move_robot(unit.id, direction)
                            ml = ml.add(direction)
                            skip_exact = goal[1] <= 2
                            if goal[1] == 1:
                                #need new direction
                                goal = state.karb_clusters[cluster_index][ml.y][ml.x]
                            break

                # replicate if can
                if unit.ability_cooldown() < ABILITY_COOLDOWN_LIMIT and len(units) < PHASE1_WORKERS_WANTED:
                    for direction in try_nearby_directions(goal[0], skip_exact):
                        if gc.can_replicate(unit.id, direction):
                            gc.replicate(unit.id, direction)
                            units.append(gc.sense_unit_at_location(ml.add(direction)))
                            break
                begin_building = len(units) >= PHASE1_WORKERS_WANTED


                bml = ml.add(goal[0])
                if blueprint_laid and goal[1] == 1:
                    bp = gc.sense_unit_at_location(bml)
                    if gc.can_build(unit.id, bp.id):
                        gc.build(unit.id, bp.id)
                    else:
                        raise Exception("Can't build even though I think I should")
                elif begin_building and gc.karbonite() > FACTORY_BUILD_COST and gc.karbonite_at(bml) < 3 and goal[1] == 1:
                    if gc.can_blueprint(unit.id, bc.UnitType.Factory, goal[0]):
                        gc.blueprint(unit.id, bc.UnitType.Factory, goal[0])
                    else:
                        raise Exception("Can't blueprint even though I think I should")
                else:
                    for direction in try_nearby_directions(goal[0]):
                        if gc.can_harvest(unit.id, direction):
                            gc.harvest(unit.id, direction)
                            break
            else:
                # control non-group-b units


def cluster_worker_score(ml, cluster):
    dist = cluster[ml.y][ml.x][1]
    val = cluster.karb
    return val / dist ** 2