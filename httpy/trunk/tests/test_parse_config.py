#!/usr/bin/env python

# Make sure we can find the module we want to test.
# =================================================

import os
import sys
if __name__ == '__main__':
    sys.path.insert(0, os.path.realpath('..'))


# Import some modules.
# ====================

import httpy
import stat
import unittest
from httpy import RequestError
from medusa import http_server, http_date
from httpyTestCase import httpyTestCase
from simpletal import simpleTAL
from xml.sax import SAXParseException


# Define the site to test against.
# ================================

def buildTestSite():
    os.mkdir('root')
    file('root/index.html', 'w')
    os.mkdir('root/about')
    os.mkdir('root/__')
    file_ = open('root/__/context.py', 'w')
    file_.write(dummy_context)
    file_.close()
    file_ = open('root/foo.pt', 'w')
    file_.write(dummy_tal)
    file_.close()



# Define our testing class.
# =========================

class TestGetTemplate(httpyTestCase):

    def setUp(self):

        # [re]build a temporary website tree in ./root
        self.removeTestSite()
        buildTestSite()

        # handler
        self.request = http_server.http_request(*self._request)
        handler_config = httpy.parse_config('')[1]
        self.handler = httpy.handler(**handler_config)


    def tearDown(self):
        self.removeTestSite()
        pass



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGetTemplate))
    return suite

if __name__ == '__main__':
    unittest.main()
