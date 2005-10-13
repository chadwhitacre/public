#!/usr/bin/env python

import hotshot
from hotshot.stats import load
import os

from TestCaseTask import DUMMY_TASK


try:
    os.system("touch index.html")
    prof = hotshot.Profile("task.prof")
    prof.runcall(DUMMY_TASK.service)
    prof.close()
finally:
    os.system("rm index.html")

stats = load("task.prof")
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(20)
os.system("rm task.prof")
