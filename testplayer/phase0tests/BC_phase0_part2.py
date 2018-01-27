# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 19:12:56 2018

@author: bunny
"""

import BC_phase0
from BC_phase0 import Point
from datetime import datetime


def get_clusters(cmap, num_clusters):
    result = [[] for i in range(num_clusters + 1)]
    for x in range(len(cmap)):
        for y in range(len(cmap[0])):
            if cmap[x][y] > 0:
                result[cmap[x][y]].append(Point(x, y))
    return result


def perform_bfs(cluster, cmap, directions):
    result = [[None for val in row] for row in cmap]
    q = []
    index = 0
    for p in cluster:
        q.append(p)
        result[p.x][p.y] = Point(0, 0)
    
    while index < len(q):
        dest = q[index]
        
        for d in directions:
            new = dest + d
            if not BC_phase0.out_of_bounds(new, cmap) and result[new.x][new.y] is None:
                result[new.x][new.y] = -d
                q.append(new)
        
        index += 1
    
    return result


def find_directions_to(clusters, cmap, directions):
    karb_finder = [None]
    for i in range(1, len(clusters)):
        karb_finder.append(perform_bfs(clusters[i], cmap, directions))
    return karb_finder


def run():
    
    num_clusters, cmap, neighbors, directions = BC_phase0.run()
    
    timer = datetime.now().microsecond
    
    clusters = get_clusters(cmap, num_clusters)
    karb_finder = find_directions_to(clusters, cmap, directions)
    
    timer = datetime.now().microsecond - timer
    
    print('Took %f milliseconds.\n' % (timer / 1000))


if __name__ == '__main__':
    run()