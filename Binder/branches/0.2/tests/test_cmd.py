if __name__ == '__main__':
    import framework

import unittest, os, pdb
from os.path import join, abspath, isdir
from StringIO import StringIO
from Binder.Binder import Binder

class TestCRUD(unittest.TestCase):

    def setUp(self):
        # ready,...
        self.out = StringIO()
        self.cleanUp()

        # ...set,...
        os.mkdir('var')
        os.mkdir('gremlin')
        self.binder = Binder(stdout=self.out)
        self.binder.output_path = abspath('gremlin')

        # ... go!

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        # clean up our filesystem
        for directory in ('var','gremlin'):
            if isdir(directory):
                test_dir = abspath(directory)
                for datafile in os.listdir(test_dir):
                    os.remove(join(test_dir, datafile))
                os.rmdir(test_dir)

    def testListWhenEmpty(self):
        self.binder.onecmd("ls")
        self.assertEqual(self.out.getvalue(), '')
        self.assertEqual(os.listdir(self.binder.var), [])
        # neither dat file nor named frags get created until we write

    def testBadInput(self):
        self.binder.onecmd("add test")
        self.assertEqual(self.out.getvalue(), "The domain name is not of " +\
                                              "the form: example.com.\n")
        self.assertEqual(os.listdir(self.binder.var), [])
        # didn't write, so still no files

    def testAddOneItem(self):
        self.binder.onecmd("add zetaweb.com")
        self.assertEqual(self.out.getvalue(), '') # silence == worked
        self.assertEqual(self.binder.domains, ['zetaweb.com'])

        self.binder.onecmd("ls")
        self.assertEqual(self.out.getvalue(), 'zetaweb.com\n')

        self.assertEqual(os.listdir(self.binder.var), ['binder.dat'])
        self.assertEqual(os.listdir(self.binder.output_path),
                                    ['named.binder.master.conf'
                                    ,'named.binder.slave.conf'])
        # now we should have both files

    def testExtraInputIsIgnored(self):
        self.binder.onecmd("add example.com server port Frank Sinatra sings the blues")
        self.assertEqual(self.binder.domains, ['example.com'])

    def testAddMultipleItems(self):
        self.binder.onecmd("add zetaweb.com")
        self.binder.onecmd("mk  thedwarf.com")
        self.binder.onecmd("add malcontents.org")
        self.binder.onecmd("mk  christyanity.com")
        self.binder.onecmd("add tesm.edu")

        domains = self.binder.domains; domains.sort()
        self.assertEqual(domains, ['christyanity.com'
                                  ,'malcontents.org'
                                  ,'tesm.edu'
                                  ,'thedwarf.com'
                                  ,'zetaweb.com'
                                   ])

    def testList(self):
        self.binder.onecmd("add zetaweb.com")
        self.binder.onecmd("mk thedwarf.com")
        self.binder.onecmd("add malcontents.org")
        self.binder.onecmd("mk christyanity.com")
        self.binder.onecmd("add tesm.edu")
        self.binder.onecmd("add zoobaz.info")
        self.binder.onecmd("add latebutlaughing.com")

        expected = """\
christyanity.com     malcontents.org  thedwarf.com  zoobaz.info
latebutlaughing.com  tesm.edu         zetaweb.com \n"""

        self.binder.onecmd("ls")
        self.assertEqual(self.out.getvalue(), expected)

    def testRemove(self):
        self.binder.onecmd("add zetaweb.com")
        self.binder.onecmd("mk thedwarf.com")
        self.binder.onecmd("add malcontents.org")
        self.binder.onecmd("mk christyanity.com")
        self.binder.onecmd("add tesm.edu")
        self.binder.onecmd("add zoobaz.info")
        self.binder.onecmd("add latebutlaughing.com")

        self.binder.onecmd("rm zetaweb.com")
        self.assertEqual(len(self.binder.domains), 6)
        self.assert_('zetaweb.com' not in self.binder.domains)

        self.binder.onecmd("rm thedwarf.com malcontents.org christyanity.com")
        self.assertEqual(len(self.binder.domains), 3)
        self.assert_('thedwarf.com' not in self.binder.domains)
        self.assert_('malcontents.org' not in self.binder.domains)
        self.assert_('christyanity.com' not in self.binder.domains)

        self.binder.onecmd("rm latebutlaughing.com")
        self.assertEqual(len(self.binder.domains), 2)
        self.assert_('latebutlaughing.com' not in self.binder.domains)

        self.assertEqual(self.binder.domains, ['tesm.edu','zoobaz.info'])

    def testFilterOnList(self):
        self.binder.onecmd("add zetaweb.com")
        self.binder.onecmd("add bloober.tv")
        self.binder.onecmd("ls zeta")
        self.assertEqual(self.binder.stdout.getvalue(),"zetaweb.com\n")

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCRUD))
    return suite

if __name__ == '__main__':
    unittest.main()