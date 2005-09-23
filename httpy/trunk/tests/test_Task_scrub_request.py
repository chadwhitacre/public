#!/usr/bin/env python

import os
import unittest

from httpy.Request import ZopeRequest
from httpy.Task import Task


class ScrubTesterTask(Task):
    def __init__(self):
        pass


INITIAL_API = [ '__doc__'
              , '__implemented__'
              , '__init__'
              , '__module__'
              , '__providedBy__'
              , '__provides__'
              , '_raw'
              , '_receiver'
              , '_tmp'
              , 'adj'
              , 'completed'
              , 'empty'
              , 'get_body'
              , 'get_headers'
              , 'get_line'
              , 'message'
              , 'method'
              , 'parse_body'
              , 'parse_line'
              , 'path'
              , 'raw'
              , 'raw_body'
              , 'raw_headers'
              , 'raw_line'
              , 'received'
              , 'set_receiver'
              , 'uri'
               ]

SCRUBBED_API = [ '__doc__'
               , '__module__'
               , 'message'
               , 'method'
               , 'path'
               , 'raw'
               , 'raw_body'
               , 'raw_headers'
               , 'raw_line'
               , 'uri'
                ]


class TestScrubRequest(unittest.TestCase):

    def setUp(self):
        self.task = ScrubTesterTask()
        self.request = Request()
        self.request.received("GET / HTTP/1.1\n\n")

    def testBasic(self):
        expected = INITIAL_API
        actual = dir(self.request)
        self.assertEqual(expected, actual)

        scrubbed = self.task.scrub_request(self.request)

        expected = SCRUBBED_API
        actual = dir(scrubbed)
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestScrubRequest))
    return suite

if __name__ == '__main__':
    unittest.main()
