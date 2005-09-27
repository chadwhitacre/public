#!/usr/bin/env python

import os
import sys
import unittest

from httpy.utils import Gaoler

from TestCaseHttpy import TestCaseHttpy





class TestUtilsGaoler(unittest.TestCase):

    def setUp(self):
        file('app.py','w').write("num = 0")

    def tearDown(self):
        os.remove('app.py')
        os.remove('app.pyc')
        del(sys.modules['app'])


    def testWithoutGaolerModuleNotReloaded(self):
        self.assert_('app' not in sys.modules)

        import app
        self.assert_('app' in sys.modules)
        self.assertEqual(app.num, 0)

        file('app.py','w').write("num = 1")
        import app
        self.assertEqual(app.num, 0)            # Still seeing the old one.
        self.assert_('app' in sys.modules)

    def testWithGaolerModuleIsReloaded(self):
        gaoler = Gaoler()

        self.assert_('app' not in sys.modules)

        gaoler.capture()
        import app
        self.assert_('app' in sys.modules)
        self.assertEqual(app.num, 0)
        gaoler.release()

        self.assert_('app' not in sys.modules)  # Not there!
        self.assertEqual(app.num, 0)            # But the name is still bound

        os.remove('app.pyc') # careful!
        file('app.py','w').write("num = 1")
        import app
        self.assertEqual(app.num, 1)            # Now we see the new one.
        self.assert_('app' in sys.modules)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtilsGaoler))
    return suite

if __name__ == '__main__':
    unittest.main()
