if __name__ == '__main__':
    import framework

import unittest, os, pdb
from os.path import join, abspath, isdir
from StringIO import StringIO
from Porter.Porter import Porter

class TestFellowIntegration(unittest.TestCase):

    def setUp(self):
        # ready,...
        self.out = StringIO()
        self.cleanUp()

        # ...set,...
        os.mkdir('var')
        self.porter = Porter(stdout=self.out)

        # ... go!

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        # clean up our filesystem
        for directory in ('var',):
            if isdir(directory):
                test_dir = abspath(directory)
                for datafile in os.listdir(test_dir):
                    os.remove(join(test_dir, datafile))
                os.rmdir(test_dir)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFellowIntegration))
    return suite

if __name__ == '__main__':
    unittest.main()