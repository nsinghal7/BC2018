# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 19:12:56 2018

@author: bunny
"""

import BC_phase0
from BC_phase0 import Point
from datetime import datetime


def get_clusters(cmap, num_clusters):
    result = [[] for i in range(num_clusters)]
    for x in range(len(cmap)):
        for y in range(len(cmap[0])):
            if cmap[x][y] != -1:
                result[cmap[x][y]].append(Point(x, y))
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
            if not BC_phase0.out_of_bounds(new, kmap) and result[new.x][new.y] is None:
                result[new.x][new.y] = -d, dist + 1
                q.append((new, dist + 1))
        
        index += 1
    
    return result


def find_directions_to(clusters, kmap, directions):
    karb_finder = []
    for i in range(len(clusters)):
        karb_finder.append(perform_bfs(clusters[i], kmap, directions))
    return karb_finder


def run():
    
    num_clusters, cmap, kmap, neighbors, directions = BC_phase0.run()
    
    timer = datetime.now().microsecond
    
    clusters = get_clusters(cmap, num_clusters)
    karb_finder = find_directions_to(clusters, kmap, directions)
    
    timer = datetime.now().microsecond - timer
    
    print('Took %f milliseconds.\n' % (timer / 1000))


if __name__ == '__main__':
    run()