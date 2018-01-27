import battlecode as bc


class Point:
    
    def __init__(self, y, x):
        self.y, self.x = y, x
    
    def __add__(self, p):
        return Point(self.y + p.y, self.x + p.x)
    
    def __neg__(self):
        return Point(-self.y, -self.x)


class Destination:
    '''
    For Destination d, d[y][x] is a tuple (dir, dist) describing the optimal path from (y, x) to d
    '''
    def __init__(self, __map__):
        self.__map__ = __map__
    
    def __getitem__(self, key):
        return self.__map__[key]


class KarbCluster(Destination):
    '''
    For KarbCluster kc, kc.karb is the amount of remaining karbonite
    '''
    def __init__(self, __map__, karb):
        super().__init__(__map__)
        self.karb = karb


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


def factory_loc_check_update(state, ml):
    