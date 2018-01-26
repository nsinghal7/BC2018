# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 22:06:01 2018

@author: bunny
"""

import json
import sys

f = open('nuclear.bc18map')

obj = json.loads(f.read())

p = obj['earth_map']['is_passable_terrain']

k = obj['earth_map']['initial_karbonite']

for i in range(len(k)):
    for j in range(len(k[0])):
        if not p[i][j]:
            k[i][j] = '#'
        elif k[i][j] > 0:
            k[i][j] = 3
        else:
            k[i][j] = '.'
        '''
        if not p[i][j]:
            k[i][j] = ' x'
        elif k[i][j] < 10:
            k[i][j] = ' %d' % k[i][j]
        '''

f = open('BC_phase0_map2.txt', 'w')

for i in range(len(k)):
    for j in range(len(k[0])):
        f.write(str(k[i][j]) + ' ')
    f.write('\n')

f.close()