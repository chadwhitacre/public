#!/usr/bin/env python

import hotshot
from hotshot.stats import load
import os
from StringIO import StringIO

from zope.server.adjustments import default_adj

from httpy.Config import Config
from httpy.Request import Request
from httpy.Task import Task


class StubServer:
    http_version_string = "HTTP/1.1"
    response_header = "stub server"
    config = Config()


class StubChannel(StringIO):
    server = StubServer()
    def close_when_done(self):
        pass


request = Request(default_adj)
request.received("GET / HTTP/1.1\r\n\r\n")
task = Task(StubChannel(), request)

try:
    os.system("touch index.html")
    prof = hotshot.Profile("task.prof")
    prof.runcall(task.service)
    prof.close()
finally:
    os.system("rm index.html")

stats = load("task.prof")
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(20)
os.system("rm task.prof")
