#!/usr/bin/env python
"""Given a doc.kml file, calculate the distance of the line.

Math help here:

    https://answers.google.com/answers/threadview?id=577262

"""
import math
import re
import sys


# Get coords from KML file
# ========================

kml = open(sys.argv[1], 'r+').read()
match = re.search("<coordinates>\n(.*?)</coordinates>", kml, re.DOTALL)
coords = [tuple([float(c) for c in d.split(',')]) for d in match.groups()[0].split()]


# Calculate assuming square geometry
# ==================================

length = 0
for i in range(len(coords)):
    j = i+1
    if j == len(coords):
        continue
    x1, y1, z1 = coords[i]
    x2, y2, z2 = coords[j]
    x_sqrd = math.pow(abs(x2-x1), 2)
    y_sqrd = math.pow(abs(y2-y1), 2)
    length += math.sqrt(x_sqrd + y_sqrd)

kilometers = float('%.02f' % (length * 85.28))
miles = float('%.02f' % (length * 85.28 * 0.621371192))
print kilometers, 'kilometers'
print miles, 'miles'
