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

        # we aren't actually going to test against a live http server
        self.porter._available_hosts = self._test_hosts
        self.porter._read_from_disk

        # some sample data
        self.porter.onecmd("add zetaweb.com bridei 8010")
        self.porter.onecmd("add example.net bridei 8020")

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

    def _test_hosts():
        return ['foo', 'bar', 'baz']
    _test_hosts = staticmethod(_test_hosts)


    def testSimpleLs(self):
        # be sure we are adding data right
        self.porter.onecmd("ls")
        self.assertEqual(self.out.getvalue(), 'example.net  zetaweb.com\n')

    def testSimpleTabCompletion(self):
        # are tabs getting expanded by TestCase?
        self.porter.onecmd("ls zet\t")
        self.assertEqual(self.out.getvalue(), 'zetaweb.com\n')

    def testNoTabCompletion(self):
        # this also works since we do startswith in ls
        self.porter.onecmd("ls zet")
        self.assertEqual(self.out.getvalue(), 'zetaweb.com\n')

#    def testAvailableHosts(self):
#        self.assertEqual(self.porter._available_hosts(),
#                         ['manually check this list against your own /etc/hosts'])

    def testAvailableWebsitesTestingStrategy(self):
        """ we aren't actually going to test against a live http server """
        self.assertEqual(self.porter._available_hosts(), ['foo', 'bar', 'baz'])

    def testAvailableWebsitesTestingStrategy(self):
        self.porter._available_hosts = self._test_hosts
        self.porter._read_from_disk()
        self.assertEqual(self.porter.websites, ['foo', 'bar', 'baz'])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFellowIntegration))
    return suite

if __name__ == '__main__':
    unittest.main()