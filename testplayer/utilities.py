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
        return self.__map__[key] if key < len(self.__map__) else None

    def __len__(self):
        return len(self.__map__)


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
    def __getattr__(self, key):
        self.key = None
        return self.key

class UnitInfo:
    info = {}

    def access(unit):
        if unit.id not in UnitInfo.info:
            UnitInfo.info[unit.id] = Container()
        return UnitInfo.info[unit.id]

    def setup():
        bc.Unit.info = UnitInfo.access


def factory_loc_check_update(state, ml):
    destmaps = []
    karbmaps = []
    for dest in state.destinations:
        worked, map = _map_check(dest, ml)
        if not worked:
            return False
        else:
            destmaps.append(map)
    for kmap in state.karb_clusters:
        worked, map = _map_check(kmap, ml)
        if not worked:
            return False
        else:
            karbmaps.append(map)
    for dest, update in zip(state.destinations, destmaps):
        _map_update(dest, update)
    for kmap, update in zip(state.karb_clusters, karbmaps):
        _map_update(kmap, update)
    return True


def _map_update(map, update, ml):
    for sy in range(3):
        y = ml.y + sy - 1
        if not (0 <= y < len(map)):
            continue
        for sx in range(3):
            x = ml.x + sx - 1
            if 0 <= x < len(map[0]):
                map[y][x] = update[sy][sx][0]


def _map_check(map, ml):
    ans = [[map[y][x] for x in range(ml.x - 1, ml.x + 2)] for y in range(ml.y - 1, ml.y + 2)]
    q = []
    pi = 0
    blocked = 0

    for y in range(3):
        for x in range(3):
            if ans[y][x] is None or y == x == 1:
                blocked += 1
                ans[y][x] = (ans[y][x], None)
            elif _points_in(y, x, ans[y][x][0]):
                pi += 1
                ans[y][x] = (ans[y][x], True)
            else:
                q.append((y, x))
                ans[y][x] = (ans[y][x], False)
    if pi == 0:
        return True, None
    index = 0
    while index < len(q) and pi > 0:
        y, x = q[index]
        index += 1
        for dy in range(-1, 2):
            ny = y + dy
            if not (0 <= ny < 3):
                continue
            for dx in range(-1, 2):
                nx = x + dx
                if 0 <= nx < len(3) and ans[ny][nx][1]:
                    ans[ny][nx] = ((Point(-dy, -dx), ans[ny][nx][0][1]), False)
                    pi -= 1
    if pi == 0:
        return True, ans
    else:
        return False, None




def _points_in(y, x, point):
    return point.y == (1-y) and point.x == (1-x)