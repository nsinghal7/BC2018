import battlecode as bc
from utilities import Point
from utilities import Path
from utilities import KarbCluster
from utilities import make_poi


def generate_kmap(self):
    start_map = []
    for row in range(self.planet_map.height):
        map_row = []
        for col in range(self.planet_map.width):
            loc = bc.MapLocation(self.planet, col, row)
            map_row.append(self.planet_map.initial_karbonite_at(loc) if self.planet_map.is_passable_terrain_at(loc) else -1)
        start_map.append(map_row)
    return start_map


def find_clusters(kmap, gap, directions):
    cmap = [[-1 for val in row] for row in kmap]
    neighbors = [[[] for val in row] for row in kmap]
    num_clusters = 0
    
    for y in range(len(kmap)):
        for x in range(len(kmap[0])):
            if kmap[y][x] > 0 and cmap[y][x] == -1:
                find_neighbors(Point(y, x), num_clusters, gap, kmap, cmap, neighbors, directions)
                num_clusters += 1
    
    return num_clusters, cmap, neighbors


def out_of_bounds(point, kmap):
    return not 0 <= point.y < len(kmap) or not 0 <= point.x < len(kmap[0]) or kmap[point.y][point.x] == -1


def find_neighbors(loc, cluster_id, gap, kmap, cmap, neighbors, directions):
    cmap[loc.y][loc.x] = cluster_id
    
    used = [[False for j in range(2 * gap + 1)] for i in range(2 * gap + 1)]
    q = []
    
    index = 0
    q.append(Path(loc))
    while index < len(q):
        path = q[index]
        dest, steps = path.dest, path.steps
        _y, _x = dest.y - loc.y + gap, dest.x - loc.x + gap
        
        if steps and kmap[dest.y][dest.x] > 0:
            neighbors[loc.y][loc.x].append(path)
            if cmap[dest.y][dest.x] == -1:
                find_neighbors(dest, cluster_id, gap, kmap, cmap, neighbors, directions)
        elif len(steps) < gap:
            for d in directions:
                ny, nx = _y + d.y, _x + d.x
                if not used[ny][nx] and not out_of_bounds(path.dest + d, kmap):
                    used[ny][nx] = True
                    q.append(path + d)
        index += 1


def get_clusters(cmap, kmap, num_clusters):
    result = [[[], 0] for i in range(num_clusters)]
    for y in range(len(cmap)):
        for x in range(len(cmap[0])):
            if cmap[y][x] != -1:
                result[cmap[y][x]][0].append(Point(y, x))
                result[cmap[y][x]][1] += kmap[y][x]
    return result


def perform_bfs(cluster, kmap, directions):
    result = [[None for val in row] for row in kmap]
    q = []
    index = 0
    for p in cluster:
        q.append((p, 0))
        result[p.y][p.x] = Point(0, 0), 0
    
    while index < len(q):
        dest, dist = q[index]
        
        for d in directions:
            new = dest + d
            if not out_of_bounds(new, kmap) and result[new.y][new.x] is None:
                result[new.y][new.x] = -d, dist + 1
                q.append((new, dist + 1))
        
        index += 1
    
    return result


def find_directions_to(clusters, kmap, directions):
    karb_clusters = []
    for i in range(len(clusters)):
        karb_clusters.append(KarbCluster(perform_bfs(clusters[i][0], kmap, directions), clusters[i][1]))
    return karb_clusters


def earth_karbonite_search(self):
    kmap, directions = self.kmap, self.directions
    
    gap = 2
    num_clusters, cmap, neighbors = find_clusters(kmap, gap, directions)
    while num_clusters > 9:
        gap += 1 # CHANGE
        num_clusters, cmap, neighbors = find_clusters(kmap, gap, directions)
    
    clusters = get_clusters(cmap, kmap, num_clusters)
    karb_clusters = find_directions_to(clusters, kmap, directions)
    
    return karb_clusters, neighbors, cmap


def add_og_poi(self):
    for unit in self.gc.my_units:
        loc = self.symmetry(unit.location.map_location())
        y, x = loc.y, loc.x
        flag = False
        for d in self.destinations:
            if d[y][x] and d[y][x][1] < 5:
                flag = True
                break
        if not flag:
            make_poi(self, Point(y, x))