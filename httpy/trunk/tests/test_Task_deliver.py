#!/usr/bin/env python

import os
import unittest
from StringIO import StringIO

from httpy.Config import ServerConfig
from httpy.Request import ZopeRequest
from httpy.Response import Response

from TestCaseHttpy import TestCaseHttpy



DUMMY_APP = """\
class Application:
   def __init__(self, config):
        return config
    def respond(self, request):
        raise "heck"
"""

from utils import DUMMY_TASK


class TestTaskRespond(TestCaseHttpy):

    def setUp(self):
        TestCaseHttpy.setUp(self)
        self.task = DUMMY_TASK()
        self.task.dev_mode = True


    # Demonstration
    # =============

    def testBasic(self):
        response = Response(200)
        response.headers['content-type'] = 'text/plain'
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'content-length: 19'
                   , u'content-type: text/plain'
                   , u'server: stub server'
                   , u''
                   , u'Greetings, program!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)


    # Response Line
    # =============

    def testBadResponseCode(self):
        response = Response(600)
        self.assertRaises(Exception, self.task.respond, response)

    def testStatusLineGetsWritten(self):
        response = Response(505)
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 505 HTTP Version not supported'
                   , u'content-length: 23'
                   , u'content-type: text/plain'
                   , u'server: stub server'
                   , u''
                   , u'Cannot fulfill request.'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testButReasonMessageCanBeOverriden(self):
        response = Response(505)
        response.body = "Just leave me alone, ok!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 505 HTTP Version not supported'
                   , u'content-length: 24'
                   , u'content-type: text/plain'
                   , u'server: stub server'
                   , u''
                   , u'Just leave me alone, ok!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)


    # Headers
    # =======

    def testHeadersAreOptional(self):
        response = Response(200)
        response.headers = {} # the default
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'content-length: 0'
                   , u'content-type: application/octet-stream'
                   , u'server: stub server'
                   , u''
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testYouCanAddArbitraryHeaders_TheyWillBeLowerCasedButWillMakeIt(self):
        response = Response(200)
        response.headers['cheese'] = 'yummy'
        response.headers['FOO'] = 'Bar'
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'cheese: yummy'
                   , u'content-length: 19'
                   , u'foo: Bar'
                   , u'content-type: application/octet-stream'
                   , u'server: stub server'
                   , u''
                   , u'Greetings, program!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testYouCanOverrideServerAndContentType(self):
        response = Response(200)
        response.headers['server'] = 'MY SERVER! MINE!'
        response.headers['content-type'] = 'cheese/yummy'
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'content-length: 19'
                   , u'content-type: cheese/yummy'
                   , u'server: MY SERVER! MINE!'
                   , u''
                   , u'Greetings, program!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testButYouCantOverrideContentLength(self):
        response = Response(200)
        response.headers['content-length'] = 50000
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'content-length: 19'
                   , u'content-type: application/octet-stream'
                   , u'server: stub server'
                   , u''
                   , u'Greetings, program!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testContentTypeDefaultsToApplicationOctetStream(self):
        response = Response(200)
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'content-length: 19'
                   , u'content-type: application/octet-stream'
                   , u'server: stub server'
                   , u''
                   , u'Greetings, program!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testExceptForNonSuccessfulRequests_InWhichCaseItIsTextPlain(self):
        response = Response(301)
        response.headers['location'] = 'http://www.google.com/'
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 301 Moved Permanently'
                   , u'content-length: 19'
                   , u'content-type: text/plain'
                   , u'location: http://www.google.com/'
                   , u'server: stub server'
                   , u''
                   , u'Greetings, program!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)




    # body
    # ====

    def testBodyNotWrittenFor304(self):
        response = Response(304)
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 304 Not modified'
                   , u'content-length: 19'
                   , u'content-type: text/plain'
                   , u'server: stub server'
                   , u''
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testBodyNotWrittenForHEADRequest(self):
        self.task.request = ZopeRequest()
        self.task.request.received("HEAD / HTTP/1.1\r\n\r\n")

        response = Response(200)
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'content-length: 19'
                   , u'content-type: application/octet-stream'
                   , u'server: stub server'
                   , u''
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testBodyIsFormattedFor537(self):
        response = Response(537)
        response.body = ('#'*20,['#'*70])
        self.task.server.deploy_mode = False
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 537 HTTPY App Dev'
                   , u'content-length: 101'
                   , u'content-type: text/plain'
                   , u'server: stub server'
                   , u''
                   , u"('####################',"
                   , u" ['######################################################################'])"
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)

    def testBut537OnlyAvailableInDevMode(self):
        response = Response(537)
        response.body = ('#'*20,['#'*70])
        self.task.dev_mode = False
        self.assertRaises(Exception, self.task.respond, response)

    def testOtherwiseBodyIsWritten(self):
        response = Response(200)
        response.body = "Greetings, program!"
        self.task.deliver(response)

        expected = [ u'HTTP/1.0 200 OK'
                   , u'content-length: 19'
                   , u'content-type: application/octet-stream'
                   , u'server: stub server'
                   , u''
                   , u'Greetings, program!'
                    ]
        actual = self.task.channel.getvalue().splitlines()
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTaskRespond))
    return suite

if __name__ == '__main__':
    unittest.main()
