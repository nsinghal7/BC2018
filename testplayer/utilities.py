import battlecode as bc
import random
import sys

MORE_THAN_MAX_MAP_DIM = 70


def end_round(state):
    print("turn over starting")
    state.gc.next_turn()
    print("turn over ending")
    sys.stdout.flush()
    sys.stderr.flush()
    print("round: %d, time left: %d" % (state.gc.round(), state.gc.get_time_left_ms()))

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
            a, b = self.steps[:], path.steps[:]
            while a and b:
                d = a[-1] + b[0]
                if not d.y and not d.x:
                    a = a[:-1]
                    b = b[1:]
                elif -1 <= d.y <= 1 and -1 <= d.x <= 1:
                    a[-1] = d
                    b = b[1:]
                else:
                    break
            return Path(path.dest, a + b)
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


def out_of_bounds(point, kmap):
    return not 0 <= point.y < len(kmap) or not 0 <= point.x < len(kmap[0]) or kmap[point.y][point.x] == -1


def make_poi(self, p):
    result = [[None for val in row] for row in self.kmap]
    q = []
    index = 0
    q.append((p, 0))
    result[p.y][p.x] = Point(0, 0), 0
    
    while index < len(q):
        dest, dist = q[index]
        
        for d in self.directions:
            new = dest + d
            if not out_of_bounds(new, self.kmap) and result[new.y][new.x] is None:
                result[new.y][new.x] = -d, dist + 1
                q.append((new, dist + 1))
        
        index += 1
    
    self.destinations.append(Destination(result))


class KarbCluster(Destination):
    '''
    For KarbCluster kc, kc.karb is the amount of remaining karbonite
    '''
    def __init__(self, __map__, karb):
        super().__init__(__map__)
        self.karb = karb


def process_worker(self, worker):
    loc = worker.location.map_location()
    y, x = loc.y, loc.x
    if self.cmap[y][x] != -1:
        harvest_cluster(self, worker)
    if worker.info().path_to_karb:
        follow_path_to_karb(self, worker)
    else:
        follow_path_to_cluster(self, worker)
    if worker.info().mode == 'random':
        random_worker(self, worker)
    #elif worker.info().mode == 'factory':
     #   factory(self, worker)
        

def follow_path_to_cluster(self, worker):
    loc = worker.location.map_location()
    y, x = loc.y, loc.x
    direc, score = Point(0, 0), 0
    for cluster in self.karb_clusters:
        s = cluster_worker_score(loc, cluster)
        if s > score:
            direc, score = cluster[y][x][0], s
    d = direc.to_Direction()
    if self.gc.is_move_ready(worker.id) and self.gc.can_move(worker.id, d):
        self.gc.move_robot(worker.id, d)

def cluster_worker_score(ml, cluster):
    if cluster[ml.y][ml.x] is None:
        return -1
    dist = cluster[ml.y][ml.x][1]
    val = cluster.karb
    if dist == 0:
        return float('inf') if cluster.karb else 0
    return val / dist ** 2


def random_worker(self, worker):
    for d in try_nearby_directions(random.choice(list(bc.Direction))):
        if self.gc.is_move_ready(worker.id) and self.gc.can_move(worker.id, d):
            self.gc.move_robot(worker.id, d)
            break
    for d in list(bc.Direction):
        if harvest(self, worker, d):
            worker.info().path_to_karb = [Point(d)]
            worker.info().mode = 'good'
            return


def location_out_of_karbonite(state, ml):
    """
    update appropriate KarbCluster to point to a neighbor, and update neighbors so this new neighbor is first.
    Returns the path to take to the nearest neighbor, or None if the cluster is empty
    """
    cid = state.cmap[ml.y][ml.x]
    cluster = state.karb_clusters[cid]
    if cluster.karb <= 0:
        return None #karbcluster empty
    neighbors = [neighbor for neighbor in state.neighbors[ml.y][ml.x]] #copy so as not to edit
    visited = {}
    orig = len(neighbors)
    index = 0
    while index < len(neighbors):
        dest = neighbors[index].dest
        if state.kmap[dest.y][dest.x] != 0:
            if index >= orig:
                # need to add to neighbors
                state.neighbors[ml.y][ml.x].insert(0, neighbors[index])
            loc = Point(ml.y, ml.x)
            for step in neighbors[index].steps:
                cluster[loc.y][loc.x] = step, cluster[loc.y][loc.x][1]
                loc = loc + step
            return neighbors[index]
        else:
            nn = state.neighbors[ml.y][ml.x]
            for n in nn:
                if (n.dest.x + n.dest.y * MORE_THAN_MAX_MAP_DIM) not in visited:
                    neighbors.append(neighbors[index] + n)
    # shouldn't happen: cluster.karb must be 0
    cluster.karb = 0
    return None


def follow_path_to_karb(self, worker):
    info = worker.info()
    path = info.path_to_karb
    if self.gc.is_move_ready(worker.id):
        for d in try_nearby_directions(path[0].to_Direction()):
            if self.gc.can_move(worker.id, d):
                self.gc.move_robot(worker.id, d)
                if len(path) == 1:
                    path[0] = path[0] + -Point(d)
                    if -1 <= path[0].y <= 1 and -1 <= path[0].x <= 1:
                        harvest(self, worker, path[0].to_Direction())
                    else:
                        info.path_to_karb = None
                        info.mode = 'random'
                else:
                    path[1] = path[1] + path[0] + -Point(d)
                    if -1 <= path[1].y <= 1 and -1 <= path[1].x <= 1:
                        new_path = path[1:]
                        info.path_to_karb = new_path
                        if len(new_path) == 1:
                            harvest(self, worker, new_path[0].to_Direction())
                    else:
                        info.path_to_karb = None
                        info.mode = 'random'
                return
        info.mode = 'random'


'''
Only call if worker is on a cluster, i.e. self.cmap[y][x] != -1
'''
def harvest_cluster(self, worker):
    harvest(self, worker, bc.Direction.Center)
    
    loc = worker.location.map_location()
    y, x = loc.y, loc.x
    if not self.kmap[y][x]:
        path = location_out_of_karbonite(self, loc)
        if path is None:
            return
        worker.info().path_to_karb = path.steps
        


def harvest(self, worker, direction):
    if self.gc.can_harvest(worker.id, direction):
        self.gc.harvest(worker.id, direction)
        loc = worker.location.map_location().add(direction)
        y, x = loc.y, loc.x
        if self.kmap[y][x] > self.gc.karbonite_at(loc):
            # OMG
            self.karb_clusters[self.cmap[y][x]].karb -= self.kmap[y][x] - self.gc.karbonite_at(loc)
            self.kmap[y][x] = self.gc.karbonite_at(loc)
        
        amt = min(self.kmap[y][x], worker.worker_harvest_amount())
        self.kmap[y][x] -= amt
        self.karb_clusters[self.cmap[y][x]].karb -= amt
        return True
    else:
        return False
    

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
    yield bc.Direction(p)

def spiral_locs(state, ml):
    x = y = 0
    dx = 0
    dy = -1
    while True:
        ax = x + ml.x
        ay = y + ml.y
        if 0 <= ay < len(state.kmap) and 0 <= ax < len(state.kmap[0]):
            yield bc.MapLocation(state.planet, ax, ay)
        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy

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

class UnitQueue:
    """ Helps determine order of movement. When a unit has to wait on another to move,
    make it rely on that other unit. If successful, it means that that unit's space will
    be available after it moves. If unsuccessful, the other unit can't move or someone
    already relies on it's space. Once all desired orderings have been made, this class
    can iterate through them, while also setting their .initialized to False so you know to
    reset them"""
    first = None
    last = None
    def __init__(self, unit, next, can_move):
        self.unit = unit
        self.relied_on_by = None
        self.next = next
        if next is None:
            UnitQueue.last = self
        self.can_move = can_move
        self.intention = intention
        self.relies_on = False
        self.initialized = True
    def rely_on_if_can(self, otherUnit):
        other = otherUnit.info().unit_queue
        if not other.can_move:
            return False, None
        elif other.relied_on_by is not None:
            return False, other.relied_on_by.unit
        else:
            other.relied_on_by = self
            self.relies_on = True
            if UnitQueue.first is self:
                next = self
                while next.relies_on:
                    next = next.next
                first = next
            return True
    def list(cls):
        start = UnitQueue.first
        next = start.next
        while next is not None or start is not None:
            while start is not None:
                if start.initialized: #if not, means already went
                    start.initialized = False
                    yield start.unit
                start = start.relied_on_by
                continue
            start = next
            if start is not None:
                next = start.next
            else:
                next = None
    def initialize_all_units(cls, state, units):
        next = None
        for unit in units[::-1]:
            # go through in reverse
            new = UnitQueue(unit, next, state.gc.is_move_ready(unit.id))
            unit.info().unit_queue = new
            next = new
        first = next
    def initialize_new_unit(cls, state, unit):
        new = UnitQueue(unit, None, state.gc.is_move_ready(unit.id))
        unit.info().unit_queue = new
        last.next = new
        last = new






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
        _map_update(dest, update, ml)
    for kmap, update in zip(state.karb_clusters, karbmaps):
        _map_update(kmap, update, ml)
    return True


def _map_update(map, update, ml):
    if update is None:
        return
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
                if 0 <= nx < 3 and ans[ny][nx][1]:
                    ans[ny][nx] = ((Point(-dy, -dx), ans[ny][nx][0][1]), False)
                    pi -= 1
    if pi == 0:
        return True, ans
    else:
        return False, None




def _points_in(y, x, point):
    return point.y == (1-y) and point.x == (1-x)