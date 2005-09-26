from StringIO import StringIO

from zope.server.adjustments import default_adj

from httpy.Config import Config
from httpy.Request import ZopeRequest
from httpy.Task import Task
from httpy.AppCache import AppCache


class StubServer:
    def __init__(self):
        self.http_version_string = "HTTP/1.0"
        self.response_header = "stub server"
        self.config = Config()
        self.apps = AppCache('development')


class StubChannel(StringIO):
    def __init__(self):
        self.server = StubServer()
    def close_when_done(self):
        pass


request = ZopeRequest(default_adj)
request.received("GET / HTTP/1.1\r\n\r\n")


def DUMMY_TASK():
    return Task(StubChannel(), request)
