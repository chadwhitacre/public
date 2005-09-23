from StringIO import StringIO

from zope.server.adjustments import default_adj

from httpy.Config import Config
from httpy.Request import Request
from httpy.Task import Task
from httpy.AppCache import AppCache


class StubServer:
    http_version_string = "HTTP/1.0"
    response_header = "stub server"
    config = Config()
    apps = AppCache('development')


class StubChannel(StringIO):
    server = StubServer()
    def close_when_done(self):
        pass


request = Request(default_adj)
request.received("GET / HTTP/1.1\r\n\r\n")


DUMMY_TASK = Task(StubChannel(), request)
