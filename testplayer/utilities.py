import battlecode as bc


class Point:
    
    def __init__(self, y, x):
        self.y, self.x = y, x
    
    def __add__(self, p):
        return Point(self.y + p.y, self.x + p.x)
    
    def __neg__(self):
        return Point(-self.y, -self.x)


class KarbCluster:
    '''
    For KarbCluster kc, kc[row][col] is a tuple (dir, dist) describing the optimal path from (row, col) to kc
    and kc.karb is the amount of remaining karbonite
    '''
    def __init__(self, map, karb):
        self.map, self.karb = map, karb
    
    def __getitem__(self, key):
        return self.map[key]


def 
    

def try_nearby_directions(goal, skip_exact=False):
    if not skip_exact:
        yield goal
    pos = True
    p = (goal.value + 1) & 7
    n = (goal.value - 1) & 7
    while not p == n:
        if pos:
            yield bc.Direction(p)
            p = (p + 1) & 7
            pos = False
        else:
            yield bc.Direction(n)
            n = (n - 1) & 7
            pos = True
    yield p

class Container:
    pass

class UnitInfo:
    info = {}

    def access(unit):
        if unit.id not in UnitInfo.info:
            UnitInfo.info[unit.id] = Container()
        return UnitInfo.info[unit.id]

    def setup():
        bc.Unit.info = UnitInfo.access