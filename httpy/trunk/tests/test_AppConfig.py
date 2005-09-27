#!/usr/bin/env python

import os
import unittest

from httpy.Config import ServerConfig
from httpy.Config import ConfigError

from TestCaseHttpy import TestCaseHttpy
from utils import DUMMY_APP


class TestSetApps(TestCaseHttpy):

    def setUp(self):
        TestCaseHttpy.setUp(self)


    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/app1')
        os.mkdir('root/app1/__')
        file('root/app1/__/app.py','w').write(DUMMY_APP)
        os.mkdir('root/app2')
        os.mkdir('root/app2/__')
        file('root/app2/__/app.py','w').write(DUMMY_APP)




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetApps))
    return suite

if __name__ == '__main__':
    unittest.main()
