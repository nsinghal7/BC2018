# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 19:40:35 2018

@author: bunny
"""

from queue import Queue
import sys
sys.setrecursionlimit(10000)

class ID:
    
    def __init__(self, x):
        self.id = x

class Pointer:
    
    def __init__(self, x):
        self.ptr = x


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
    cur_id = 0
    
    for x in range(len(kmap)):
        for y in range(len(kmap[0])):
            if kmap[x][y] > 0:
                if not cmap[x][y]:
                    num_clusters += 1
                    cur_id += 1
                    cmap[x][y] = Pointer(ID(cur_id))
                num_clusters -= find_neighbors(Point(x, y), gap, kmap, cmap, neighbors, directions)
    
    cmap = [[val.ptr.id if type(val) == Pointer else val for val in row] for row in cmap]
    
    return num_clusters, cmap, neighbors


def out_of_bounds(point, kmap):
    return not 0 <= point.x < len(kmap) or not 0 <= point.y < len(kmap[0]) or kmap[point.x][point.y] == -1


def find_neighbors(loc, gap, kmap, cmap, neighbors, directions):
    used = [[False for j in range(2 * gap + 1)] for i in range(2 * gap + 1)]
    q = Queue()
    repeats = 0
    
    q.put(Path(loc))
    while not q.empty():
        path = q.get()
        _x, _y = path.dest.x - loc.x + gap, path.dest.y - loc.y + gap
        if used[_x][_y] or out_of_bounds(path.dest, kmap):
            continue
        used[_x][_y] = True
        
        if path.steps and kmap[path.dest.x][path.dest.y] > 0:
            neighbors[loc.x][loc.y].append(path)
            if cmap[path.dest.x][path.dest.y]:
                if cmap[path.dest.x][path.dest.y].ptr.id != cmap[loc.x][loc.y].ptr.id:
                    print(loc.x, loc.y, cmap[loc.x][loc.y].ptr.id, path.dest.x, path.dest.y, cmap[path.dest.x][path.dest.y].ptr.id)
                    cmap[path.dest.x][path.dest.y].ptr.id = cmap[loc.x][loc.y].ptr.id
                    repeats += 1
            else:
                cmap[path.dest.x][path.dest.y] = cmap[loc.x][loc.y]
        elif len(path.steps) < gap:
            for d in directions:
                q.put(path + d)
    return repeats
    

if __name__ == '__main__':
    kmap = read('BC_phase0_map2.txt')
    
    gap = 2
    num_clusters, cmap, neighbors = find_clusters(kmap, gap)
    while num_clusters > 4:
        gap += 2
        num_clusters, cmap, neighbors = find_clusters(kmap, gap)
    
    f = open('BC_phase0_map2_out.txt', 'w')
    
    f.write('%d %d\n' % (gap, num_clusters))
    for row in cmap:
        for val in row:
            f.write('#' if val == -1 else '.' if val == 0 else str(val))
            f.write(' ')
        f.write('\n')
    
    f.close()