#!/usr/bin/env python

import os
import unittest
from StringIO import StringIO

from httpy.Config import Config
from httpy.Response import Response

from httpyTestCase import httpyTestCase


DUMMY_APP = """\
class Transaction:
   def __init__(self, config):
        return config
    def process(self, request):
        raise "heck"
"""


from TestCaseTask import DUMMY_TASK


class TestTaskRespond(httpyTestCase):

    def setUp(self):
        self.task = DUMMY_TASK
        self.task.out = StringIO()
        os.mkdir('root')

        os.environ['HTTPY_VERBOSITY'] = '0'


    def testDontUseMutableObjectsAsDefaults(self):
        """Demonstraion of a gotcha.

        Since method parameter defaults are evaluated at import time, two
        instances of a class will have an identical default value if that value
        is mutable. Changes to that value will affect all instances of the
        class.

        Response had this bug.

        """

        # Define a class and instantiate it a couple times.
        # =================================================

        class foo:
            def __init__(self, bar={}, bloo=[], yay=0, blam=None):
                self.bar = bar
                self.bloo = bloo
                self.yay = yay
                self.blam = blam
        foo1 = foo()
        foo2 = foo()


        # Mess with the attributes on the first instance.
        # ===============================================

        foo1.bar['baz'] = 'buz'
        foo1.bloo.append('zippy')
        foo1.yay = 1
        foo1.blam = True


        # Changes to the mutable attrs also appear on the second instance!
        # ================================================================

        self.assertEqual(foo1.bar, foo2.bar)        # mutable
        self.assertEqual(foo1.bloo, foo2.bloo)      # mutable
        self.assertNotEqual(foo1.yay, foo2.yay)     # immutable
        self.assertNotEqual(foo1.blam, foo2.blam)   # immutable


        # But this doesn't happen if we override the default on construction.
        # ===================================================================

        foo3 = foo({})
        self.assertNotEqual(foo1.bar, foo3.bar)     # mutable, overriden
        self.assertEqual(foo1.bloo, foo3.bloo)      # mutable, not overriden



    def tearDown(self):
        os.rmdir('root')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTaskRespond))
    return suite

if __name__ == '__main__':
    unittest.main()
