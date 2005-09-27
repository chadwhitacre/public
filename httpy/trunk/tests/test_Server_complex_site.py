#!/usr/bin/env python

import os
import unittest
from httplib import HTTPConnection
from httplib import HTTPResponse as ClientHTTPResponse

from httpy.Config import Config
from httpy.Server import Server

from TestCaseHttpy import TestCaseHttpy


# shared
# ======

TemplateLanguage = """\
def fill(template, value):
    return template % value
"""

App = """\
from httpy import DefaultApp as app
class Transaction(app.Transaction):
    pass
"""



# Foo
# ===

FooMasterTemplate = "You requested this resource: %s"

FooApp = """\
import os

from httpy.Response import Response
from TLang import fill

class Transaction:

    def __init__(self, config):
        self.config = config

    def process(self, request):
        _path = os.path.join(self.config.__, 'master.template')
        master = file(_path).read()
        response = Response(200)
        response.body = fill(master, request.path)
        raise response

"""


# Bar
# ===

BarMasterTemplate = "MUAHAHA(%s)HAHAHHA!!!!!!!!!!!!!!1"

BarApp = """\
import os

from httpy.Response import Response
import TLang

class Transaction:

    def __init__(self, config):
        self.config = config

    def process(self, request):

        _path = os.path.join(self.config.__, 'master.template')
        master = file(_path).read()
        response = Response(200)
        response.body = TLang.fill(master, os.name)
        raise response

"""



class TestServer(TestCaseHttpy):

    server = True
    verbosity = 0

    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w').write("Greetings, program!")

        os.mkdir('root/__')
        file('root/__/app.py', 'w').write(App)
        os.mkdir('root/__/site-packages')
        file('root/__/site-packages/TLang.py','w').write(TemplateLanguage)

        os.mkdir('root/foo')
        os.mkdir('root/foo/__')
        file('root/foo/__/master.template', 'w').write(FooMasterTemplate)
        file('root/foo/__/app.py', 'w').write(FooApp)

        os.mkdir('root/bar')
        os.mkdir('root/bar/__')
        file('root/bar/__/master.template', 'w').write(BarMasterTemplate)
        file('root/bar/__/app.py', 'w').write(BarApp)


    def testBasic(self):
        conn = HTTPConnection('localhost', self.port)
        conn.request("GET", "/", '', {'Accept':'text/plain'})
        expected = "Greetings, program!"
        actual = conn.getresponse().read()
        self.assertEqual(expected, actual)

    def testFooApp(self):
        conn = HTTPConnection('localhost', self.port)
        conn.request("GET", "/foo/", '', {'Accept':'text/plain'})
        expected = "You requested this resource: /foo/"
        actual = conn.getresponse().read()
        self.assertEqual(expected, actual)

    def testBarApp(self):
        conn = HTTPConnection('localhost', self.port)
        conn.request("GET", "/bar/", '', {'Accept':'text/plain'})
        expected = "MUAHAHA(%s)HAHAHHA!!!!!!!!!!!!!!1" % os.name
        actual = conn.getresponse().read()
        self.assertEqual(expected, actual)

    def testThemBothAtOnce(self):
        conn1 = HTTPConnection('localhost', self.port)
        conn2 = HTTPConnection('localhost', self.port)
        conn1.request("GET", "/foo/", '', {'Accept':'text/plain'})
        conn2.request("GET", "/bar/", '', {'Accept':'text/plain'})

        expected = "You requested this resource: /foo/"
        actual = conn1.getresponse().read()
        self.assertEqual(expected, actual)

        expected = "MUAHAHA(%s)HAHAHHA!!!!!!!!!!!!!!1" % os.name
        actual = conn2.getresponse().read()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestServer))
    return suite

if __name__ == '__main__':
    unittest.main()
