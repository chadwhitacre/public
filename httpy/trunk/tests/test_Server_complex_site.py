#!/usr/bin/env python

import os
import unittest
from httplib import HTTPConnection
from httplib import HTTPResponse as ClientHTTPResponse

from httpy.Config import Config
from httpy.Server import Server

from TestCaseHttpy import TestCaseHttpy


# Foo
# ===

FooTemplateLanguage = """\
def fill(template, value):
    return template % value
"""

FooMasterTemplate = "You requested this resource: %s"

Foo = """\
import os

from httpy.Response import Response
import TemplateLanguage

class Transaction:

    def __init__(self, config):
        self.config = config

    def process(self, request):
        _path = os.path.join(self.config['__'], 'master.template')
        master = file(_path).read()
        response = Response(200)
        response.body = TemplateLanguage.fill(master, request.path)
        raise response
"""


# Bar
# ===

BarTemplateLanguage = """\
def fill(template, value):
    return template % "MUAHAHAHAHAHHA!!!!!!!!!!!!!!1"
"""

BarMasterTemplate = "You asked for this resource: %s"

Bar = """\
import os

from httpy.Response import Response
import TemplateLanguage

class Transaction:

    def __init__(self, config):
        self.config = config

    def process(self, request):
        _path = os.path.join(self.config['__'], 'master.template')
        master = file(_path).read()
        response = Response(200)
        response.body = TemplateLanguage.fill(master, request.path)
        raise response
"""



class TestServer(TestCaseHttpy):

    server = True
    verbosity = 0

    def buildTestSite(self):
        
        file('root/index.html', 'w').write("Greetings, program!")
        os.mkdir('root/foo')
        file('root/foo/index.html', 'w').write("Greetings, foo!")
        os.mkdir('root/foo/__')
        file('root/foo/__/TemplateLanguage.py', 'w').write(FooTemplateLanguage)
        file('root/foo/__/master.template', 'w').write(FooMasterTemplate)
        file('root/foo/__/app.py', 'w').write(Foo)
        os.mkdir('root/bar')
        os.mkdir('root/bar/__')
        file('root/bar/__/TemplateLanguage.py', 'w').write(BarTemplateLanguage)
        file('root/bar/__/master.template', 'w').write(BarMasterTemplate)
        file('root/bar/__/app.py', 'w').write(Bar)


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
        expected = "You asked for this resource: MUAHAHAHAHAHHA!!!!!!!!!!!!!!1"
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

        expected = "You asked for this resource: MUAHAHAHAHAHHA!!!!!!!!!!!!!!1"
        actual = conn2.getresponse().read()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestServer))
    return suite

if __name__ == '__main__':
    unittest.main()
