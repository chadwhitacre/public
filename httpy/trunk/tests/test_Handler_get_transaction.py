#!/usr/bin/env python

import imp
import os
import unittest

import httpy.app
from httpy.HandlerRequestMixin import HandlerRequestMixin
from httpy.Response import Response
from httpyTestCase import httpyTestCase


DUMMY_APP_BAD = """\
class Transaction:
    def __init__(self, config):
        self.config = config
"""

DUMMY_APP = """\
from httpy.Response import Response
class Transaction:
    def __init__(self, config):
        self.config = config
    def process(self, request):
        raise Response(200)
"""


class TestTranslate(httpyTestCase):

    server = False
    siteroot = os.path.join(os.path.realpath('.'),'root')

    def setUp(self):
        httpyTestCase.setUp(self)
        self.mixin = HandlerRequestMixin()
        self.config = {}
        self.config['apps'] = [ '/app1'
                              , '/app2'
                              , '/app3'
                              , '/app4'
                              , '/app5'
                              , '/app6'
                               ]
        self.config['ip'] = ''
        self.config['mode'] = 'development'
        self.config['port'] = 8080
        self.config['root'] = 'root'
        self.config['verbosity'] = 1

        os.environ['HTTPY_VERBOSITY'] = '0'


    def buildTestSite(self):
        os.mkdir('root')
        file('root/index.html', 'w').write('Greetings, program!')

    def test0Basic(self):
        path = '/'
        expected = httpy.app.Transaction
        actual = self.mixin.get_transaction(self.config, path)
        self.assert_(isinstance(actual, expected))

    def test1NoMagicDir(self):
        os.mkdir('root/app1')
        path = '/app1'
        expected = httpy.app.Transaction
        actual = self.mixin.get_transaction(self.config, path)
        self.assert_(isinstance(actual, expected))

    def test2MagicDirButNoApp(self):
        os.mkdir('root/app2')
        os.mkdir('root/app2/__')
        path = '/app2'
        expected = httpy.app.Transaction
        actual = self.mixin.get_transaction(self.config, path)
        self.assert_(isinstance(actual, expected))

    def test3MagicDirAndAppButNoTransaction(self):
        os.mkdir('root/app3')
        os.mkdir('root/app3/__')
        file('root/app3/__/app.py', 'w')
        path = '/app3'
        expected = httpy.app.Transaction
        actual = self.mixin.get_transaction(self.config, path)
        self.assert_(isinstance(actual, expected))

    def test4MagicDirAndAppAndTransactionButNoProcess(self):
        os.mkdir('root/app4')
        os.mkdir('root/app4/__')
        file('root/app4/__/app.py', 'w').write(DUMMY_APP_BAD)
        path = '/app4'
        expected = httpy.app.Transaction
        actual = self.mixin.get_transaction(self.config, path)
        self.assert_(isinstance(actual, expected))

    def test5MagicDirAndAppAndTransactionAndProcess(self):
        os.mkdir('root/app5')
        os.mkdir('root/app5/__')
        file('root/app5/__/app.py', 'w').write(DUMMY_APP)
        path = '/app5'

        #fp, pathname, description = imp.find_module('app', ['root/app5/__'])
        #expected = imp.load_module('app', fp, pathname, description).Transaction
        # THIS DIDN'T WORK

        actual = self.mixin.get_transaction(self.config, path)
        self.assert_(not isinstance(actual, httpy.app.Transaction))

    def test6GoodAppAsPackage(self):
        os.mkdir('root/app6')
        os.mkdir('root/app6/__')
        os.mkdir('root/app6/__/app')
        file('root/app6/__/app/__init__.py', 'w').write(DUMMY_APP)
        path = '/app6'

        actual = self.mixin.get_transaction(self.config, path)
        self.assert_(not isinstance(actual, httpy.app.Transaction))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTranslate))
    return suite

if __name__ == '__main__':
    unittest.main()
