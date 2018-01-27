import battlecode as bc
from utilities import Point
from utilities import Path
from utilities import KarbCluster


def generate_kmap(self):
    planet_map = self.gc.starting_map(self.planet)
    start_map = []
    for row in range(planet_map.height):
        map_row = []
        for col in range(planet_map.width):
            loc = bc.MapLocation(self.planet, row, col)
            map_row.append(planet_map.initial_karbonite_at(loc) if planet_map.is_passable_terrain_at(loc) else -1)
        start_map.append(map_row)
    return start_map


def find_clusters(kmap, gap, directions):
    cmap = [[-1 for val in row] for row in kmap]
    neighbors = [[[] for val in row] for row in kmap]
    num_clusters = 0
    
    for x in range(len(kmap)):
        for y in range(len(kmap[0])):
            if kmap[x][y] > 0 and cmap[x][y] == -1:
                find_neighbors(Point(x, y), num_clusters, gap, kmap, cmap, neighbors, directions)
                num_clusters += 1
    
    return num_clusters, cmap, neighbors


def out_of_bounds(point, kmap):
    return not 0 <= point.x < len(kmap) or not 0 <= point.y < len(kmap[0]) or kmap[point.x][point.y] == -1


def find_neighbors(loc, cluster_id, gap, kmap, cmap, neighbors, directions):
    cmap[loc.x][loc.y] = cluster_id
    
    used = [[False for j in range(2 * gap + 1)] for i in range(2 * gap + 1)]
    q = []
    
    index = 0
    q.append(Path(loc))
    while index < len(q):
        path = q[index]
        dest, steps = path.dest, path.steps
        _x, _y = dest.x - loc.x + gap, dest.y - loc.y + gap
        
        if steps and kmap[dest.x][dest.y] > 0:
            neighbors[loc.x][loc.y].append(path)
            if cmap[dest.x][dest.y] == -1:
                find_neighbors(dest, cluster_id, gap, kmap, cmap, neighbors, directions)
        elif len(steps) < gap:
            for d in directions:
                nx, ny = _x + d.x, _y + d.y
                if not used[nx][ny] and not out_of_bounds(path.dest + d, kmap):
                    used[nx][ny] = True
                    q.append(path + d)
        index += 1


def get_clusters(cmap, kmap, num_clusters):
    result = [([], 0) for i in range(num_clusters)]
    for x in range(len(cmap)):
        for y in range(len(cmap[0])):
            if cmap[x][y] != -1:
                result[cmap[x][y]][0].append(Point(x, y))
                result[cmap[x][y]][1] += kmap[x][y]
    return result


def perform_bfs(cluster, kmap, directions):
    result = [[None for val in row] for row in kmap]
    q = []
    index = 0
    for p in cluster:
        q.append((p, 0))
        result[p.x][p.y] = Point(0, 0), 0
    
    while index < len(q):
        dest, dist = q[index]
        
        for d in directions:
            new = dest + d
            if not out_of_bounds(new, kmap) and result[new.x][new.y] is None:
                result[new.x][new.y] = -d, dist + 1
                q.append((new, dist + 1))
        
        index += 1
    
    return result


def find_directions_to(clusters, kmap, directions):
    karb_clusters = []
    for i in range(len(clusters)):
        karb_clusters.append(KarbCluster(perform_bfs(clusters[i][0], kmap, directions), clusters[i][1]))
    return karb_clusters


def earth_karbonite_search(self):
    kmap, directions = self.start_map, self.directions
    
    gap = 2
    num_clusters, cmap, neighbors = find_clusters(kmap, gap, directions)
    while num_clusters > 9:
        gap += 1 # CHANGE
        num_clusters, cmap, neighbors = find_clusters(kmap, gap, directions)
    
    clusters = get_clusters(cmap, kmap, num_clusters)
    karb_clusters = find_directions_to(clusters, kmap, directions)
    
    return karb_clusters, neighbors