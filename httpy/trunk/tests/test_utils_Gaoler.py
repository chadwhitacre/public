#!/usr/bin/env python

import imp
import os
import unittest

from httpy.utils import Gaoler

from TestCaseHttpy import TestCaseHttpy


class TestUtilsGaoler(TestCaseHttpy):

    def buildTestSite(self):
        os.mkdir('root')
        os.mkdir('root/0')
        file('root/0/app.py','w').write("num = 0")
        os.mkdir('root/1')
        file('root/1/app.py','w').write("num = 1")
        os.mkdir('root/2')
        file('root/2/app.py','w').write("num = 2")


    def testPathBasic(self):
        import sys
        self.assert_('root/0' not in sys.path)

        gaoler = Gaoler()
        gaoler.capture_path('root/0')
        self.assert_('root/0' in sys.path)
        gaoler.release_path()

        self.assert_('root/0' not in sys.path)


    def testModulesBasic(self):
        import sys
        self.assert_('app' not in sys.modules)

        gaoler = Gaoler()
        gaoler.capture('root/0')

        import app
        self.assertEqual(app.num, 0)
        self.assert_('app' in sys.modules)

        gaoler.release()

        self.assertEqual(app.num, 0)
        self.assert_('app' not in sys.modules)


    def testDifferentModuleAndOtherTestDoesntScrewThingsUp(self):
        import sys
        self.assert_('app' not in sys.modules)

        gaoler = Gaoler()
        gaoler.capture('root/1')

        import app
        self.assertEqual(app.num, 1)
        self.assert_('app' in sys.modules)

        gaoler.release()

        self.assertEqual(app.num, 1)
        self.assert_('app' not in sys.modules)


    def testNowTheRealTest_TwoModulesSameTest(self):
        import sys
        self.assert_('app' not in sys.modules)


        # Module 0

        gaoler = Gaoler()
        gaoler.capture('root/0')

        import app
        self.assertEqual(app.num, 0)
        self.assert_('app' in sys.modules)

        gaoler.release()

        self.assertEqual(app.num, 0)
        self.assert_('app' not in sys.modules)


        # Module 1

        gaoler = Gaoler()
        gaoler.capture('root/1')

        import app
        self.assertEqual(app.num, 1)
        self.assert_('app' in sys.modules)

        gaoler.release()

        self.assertEqual(app.num, 1)
        self.assert_('app' not in sys.modules)


    def testAliasing(self):
        import sys
        self.assert_('app' not in sys.modules)

        gaoler = Gaoler()
        gaoler.capture('root/0')
        import app as app0
        gaoler.release()

        gaoler = Gaoler()
        gaoler.capture('root/1')
        import app as app1
        gaoler.release()

        gaoler = Gaoler()
        gaoler.capture('root/2')
        import app as app2
        gaoler.release()

        self.assertEqual(app0.num, 0)
        self.assertEqual(app1.num, 1)
        self.assertEqual(app2.num, 2)


    def testOverriding(self):
        import sys
        self.assert_('app' not in sys.modules)

        gaoler = Gaoler()
        gaoler.capture('root/0')
        import app
        gaoler.release()

        self.assertEqual(app.num, 0)


        gaoler = Gaoler()
        gaoler.capture('root/1')
        import app
        gaoler.release()

        self.assertEqual(app.num, 1)


    def testWeCantJustDoThisWithExecSinceDictCopyKeepsMutableValues(self):
        import sys
        _locals = locals().copy()
        _locals['sys'].path = []
        self.assertEqual(_locals['sys'].path, locals()['sys'].path)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestUtilsGaoler))
    return suite

if __name__ == '__main__':
    unittest.main()
