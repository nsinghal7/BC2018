# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 19:40:35 2018

@author: bunny
"""

from datetime import datetime


class Point:
    
    def __init__(self, x, y):
        self.x, self.y = x, y
    
    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)


class Path:
    
    def __init__(self, dest, steps = []):
        self.dest, self.steps = dest, steps
    
    def __add__(self, step):
        return Path(self.dest + step, self.steps + [step])


def read(file):
    return [[-1 if val == '#' else 0 if val == '.' else int(val) for val in line.split()] for line in open(file)]


def find_clusters(kmap, gap):
    directions = [Point(dx, dy) for dx in range(-1, 2) for dy in range(-1, 2) if dx or dy]
    cmap = [[-1 if val == -1 else 0 for val in row] for row in kmap]
    neighbors = [[[] for val in row] for row in kmap]
    num_clusters = 0
    
    for x in range(len(kmap)):
        for y in range(len(kmap[0])):
            if kmap[x][y] > 0 and not cmap[x][y]:
                num_clusters += 1
                find_neighbors(Point(x, y), num_clusters, gap, kmap, cmap, neighbors, directions)
    
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
        _x, _y = path.dest.x - loc.x + gap, path.dest.y - loc.y + gap
        
        if path.steps and kmap[path.dest.x][path.dest.y] > 0:
            neighbors[loc.x][loc.y].append(path)
            if not cmap[path.dest.x][path.dest.y]:
                find_neighbors(path.dest, cluster_id, gap, kmap, cmap, neighbors, directions)
        elif len(path.steps) < gap:
            for d in directions:
                if not used[_x + d.x][_y + d.y] and not out_of_bounds(path.dest + d, kmap):
                    used[_x + d.x][_y + d.y] = True
                    q.append(path + d)
        index += 1
    

if __name__ == '__main__':
    kmap = read('BC_phase0_map2.txt')
    
    timer = datetime.now().microsecond
    #pr = cProfile.Profile()
    #pr.enable()
    
    gap = 2
    num_clusters, cmap, neighbors = find_clusters(kmap, gap)
    while num_clusters > 4:
        gap += 1
        num_clusters, cmap, neighbors = find_clusters(kmap, gap)
    
    timer = datetime.now().microsecond - timer
    #pr.disable()
    #sortby = 'cumulative'
    #ps = pstats.Stats(pr).sort_stats(sortby)
    #ps.print_stats()
    
    f = open('BC_phase0_map2_out.txt', 'w')
    
    f.write('%d %d\n' % (gap, num_clusters))
    f.write('Took %f milliseconds.\n' % (timer / 1000))
    for row in cmap:
        for val in row:
            f.write('#' if val == -1 else '.' if val == 0 else str(val))
            f.write(' ')
        f.write('\n')
    
    f.close()