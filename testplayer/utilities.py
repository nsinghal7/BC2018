import battlecode as bc


class Point:
    
    # Ex: Point(bc.Direction.Southeast) => Point(-1, 1)
    def __init__(self, y, x = None):
        if x is None:
            self.y, self.x = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (0, 0)][y.value]
        else:
            self.y, self.x = y, x
    
    # Ex: Point(-1, 1).to_Direction() => bc.Direction.Southeast
    def to_Direction(self):
        return [[bc.Direction.Center, bc.Direction.East, bc.Direction.West],
                [bc.Direction.North, bc.Direction.Northeast, bc.Direction.Northwest],
                [bc.Direction.South, bc.Direction.Southeast, bc.Direction.Southwest]][self.y][self.x]
    
    def __add__(self, p):
        return Point(self.y + p.y, self.x + p.x)
    
    def __neg__(self):
        return Point(-self.y, -self.x)
    

class Path:
    
    def __init__(self, dest, steps = []):
        self.dest, self.steps = dest, steps
    
    def __add__(self, path):
        if type(path) == Path:
            
        else:
            return Path(self.dest + path, self.steps + [path])


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


'''
Only call if worker is on a cluster, i.e. self.cmap[y][x] != -1
'''
def harvest_cluster(self, worker):
    harvest(self, worker, bc.Direction.Center)
    
    loc = worker.location.map_location()
    y, x = loc.y, loc.x
    if not self.kmap[y][x]:
        


def harvest(self, worker, direction):
    if self.gc.can_harvest(worker.id, direction):
        self.gc.harvest(worker.id, direction)
        loc = worker.location.map_location().add(direction)
        y, x = loc.y, loc.x
        
        if self.kmap[y][x] > self.gc.karbonite_at(loc):
            # OMG
            self.kmap[y][x] = self.gc.karbonite_at(loc)
        
        amt = min(self.kmap[y][x], worker.worker_harvest_amount())
        self.kmap[y][x] -= amt
        self.karb_clusters[self.cmap[y][x]].karb -= amt
    

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