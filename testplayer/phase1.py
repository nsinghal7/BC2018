def replicate_workers_phase(state):
    units = gc.units()
    factory_loc = units[0].location.map_location()
    replicate_id = units[0].id

    while True:
        for unit in units():
            if unit.id != state.replicate_id:
                # collect efficiently, don't care about direction
                direction, hdir = towards_karbonite(unit.location.map_location())
                if direction != bc.Direction.Center:
                    pass


def towards_karbonite(ml):
    # get direction to move, direction from there to max karbonite
    (xmax, ymax), (x2, y2) = highest_2_karbonite_in_25(ml)
    if abs(ymax) != 2:
        # freedom to choose y pos
        if (ymax > 0) == (y2 > 0):
            dy = ymax
        else:
            dy = 0
    else:
        dy = ymax >> 1 # go towards ymax
    if abs(xmax) != 2:
        if (xmax > 0) == (x2 > 0):
            dx = xmax
        else:
            dx = 0
    else:
        dx = xmax >> 1
    return directionMap[dy + 1][dx + 1], directionMap[ymax - dy + 1][xmax - dx + 1]

def highest_2_karbonite_in_25(ml):
    kmax, xmax, ymax = -1, None, None
    k2, x2, y2 = -1, None, None
    for x in range(-2, 3):
        for y in range(-2, 3):
            k = gc.karbonite_at(ml.translate(x, y))
            if k > kmax:
                k2, x2, y2 = kmax, xmax, ymax
                kmax, xmax, ymax = k, x, y
            else:
                k2, x2, y2 = k, x, y
    return (xmax, ymax), (x2, y2)