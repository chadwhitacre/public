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
        self.binder.gremlin = abspath('gremlin')

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
        self.assertEqual(os.listdir(self.binder.var), ['rewrite.db'])
        # db gets created when we try to read in data, frag file not until we
        #  write

    def testBadInput(self):
        self.binder.onecmd("add test")
        self.assertEqual(self.out.getvalue(), "We need a domain name, a " +\
                                              "server name, and a port " +\
                                              "number.\n")
        self.assertEqual(os.listdir(self.binder.var), ['rewrite.db'])
        # didn't write, so still just one file

    def testAddOneItem(self):
        self.binder.onecmd("add zetaweb.com alpin 8010")
        self.binder.onecmd("ls")
        self.assertEqual(self.binder.domains, {'zetaweb.com':'alpin:8010'})
        self.assertEqual(self.binder.aliases, {'alpin:8010':['zetaweb.com']})
        self.assertEqual(self.out.getvalue(), 'zetaweb.com\n')
        self.assertEqual(os.listdir(self.binder.var), ['rewrite.db'
                                                      ,'rewrite.db.old'])
        self.assertEqual(os.listdir(self.binder.var), ['rewrite.db'
                                                      ,'rewrite.db.old'])
        # now we should have both files, plus a backup!
        # to be really thorough we should reload the backup and make sure it works

    def testExtraInputIsIgnored(self):
        self.binder.onecmd("add example.com server port Frank Sinatra sings the blues")
        self.assertEqual(self.binder.domains, {"example.com":"server:port"})

    def testAddMultipleItems(self):
        self.binder.onecmd("add zetaweb.com alpin 8010")
        self.binder.onecmd("mk  thedwarf.com duder 8020")
        self.binder.onecmd("add malcontents.org duder 8020")
        self.binder.onecmd("mk  christyanity.com duder 8020")
        self.binder.onecmd("add tesm.edu underbird 8310")

        domains = self.binder.domains.keys(); domains.sort()
        self.assertEqual(domains, ['christyanity.com'
                                  ,'malcontents.org'
                                  ,'tesm.edu'
                                  ,'thedwarf.com'
                                  ,'zetaweb.com'
                                   ])

        aliases = self.binder.aliases.keys(); aliases.sort()
        self.assertEqual(aliases, ['alpin:8010'
                                  ,'duder:8020'
                                  ,'underbird:8310'
                                   ])

        multi_domains = self.binder.aliases['duder:8020']
        multi_domains.sort()
        self.assertEqual(multi_domains, ['christyanity.com'
                                        ,'malcontents.org'
                                        ,'thedwarf.com'
                                         ])

        single_domain = self.binder.aliases['alpin:8010']
        self.assertEqual(single_domain, ['zetaweb.com'])

        single_domain = self.binder.aliases['underbird:8310']
        self.assertEqual(single_domain, ['tesm.edu'])

    def testList(self):
        self.binder.onecmd("add zetaweb.com alpin 8010")
        self.binder.onecmd("mk thedwarf.com duder 8020")
        self.binder.onecmd("add malcontents.org duder 8020")
        self.binder.onecmd("mk christyanity.com duder 8020")
        self.binder.onecmd("add tesm.edu underbird 8310")
        self.binder.onecmd("add zoobaz.info dummy 80")
        self.binder.onecmd("add latebutlaughing.com dummy 80")

        expected = """\
christyanity.com     malcontents.org  thedwarf.com  zoobaz.info
latebutlaughing.com  tesm.edu         zetaweb.com \n"""

        self.binder.onecmd("ls")
        self.assertEqual(self.out.getvalue(), expected)

    def testRemove(self):
        self.binder.onecmd("add zetaweb.com alpin 8010")
        self.binder.onecmd("mk thedwarf.com duder 8020")
        self.binder.onecmd("add malcontents.org duder 8020")
        self.binder.onecmd("mk christyanity.com duder 8020")
        self.binder.onecmd("add tesm.edu underbird 8310")
        self.binder.onecmd("add zoobaz.info dummy 80")
        self.binder.onecmd("add latebutlaughing.com dummy 80")

        self.binder.onecmd("rm zetaweb.com")
        self.assertEqual(len(self.binder.domains), 6)
        self.assert_('zetaweb.com' not in self.binder.domains)
        domains = []
        for w in self.binder.aliases:
            domains += self.binder.aliases[w]
        self.assertEqual(len(domains), 6)
        self.assert_('zetaweb.com' not in domains)

        self.binder.onecmd("rm thedwarf.com malcontents.org christyanity.com")
        self.assertEqual(len(self.binder.domains), 3)
        self.assert_('thedwarf.com' not in self.binder.domains)
        self.assert_('malcontents.org' not in self.binder.domains)
        self.assert_('christyanity.com' not in self.binder.domains)
        domains = []
        for w in self.binder.aliases:
            domains += self.binder.aliases[w]
        self.assertEqual(len(domains), 3)
        self.assert_('thedwarf.com' not in domains)
        self.assert_('malcontents.org' not in domains)
        self.assert_('christyanity.com' not in domains)

        self.binder.onecmd("rm latebutlaughing.com")
        self.assertEqual(len(self.binder.domains), 2)
        self.assert_('latebutlaughing.com' not in self.binder.domains)
        domains = []
        for w in self.binder.aliases:
            domains += self.binder.aliases[w]
        self.assertEqual(len(domains), 2)
        self.assert_('latebutlaughing.com' not in domains)

        domains = self.binder.domains.keys(); domains.sort()
        self.assertEqual(domains, ['tesm.edu','zoobaz.info'])

    def testDoubleUpBug(self):
        self.binder.onecmd("add ugandapartners.org bridei 8010")
        self.binder.onecmd("mv ugandapartners.org bridei 8110")
        self.assertEqual(self.binder.aliases['bridei:8010'], [])

        self.binder.onecmd("mv ugandapartners.org bridei 8010")
        self.assertEqual(self.binder.aliases['bridei:8010'], ['ugandapartners.org'])

    def testDoubleUpBugAgain(self):
        self.binder.onecmd("add zetaweb.com bridei 8090")
        self.binder.onecmd("add ugandapartners.org bridei 8090")
        self.assertEqual(self.binder.aliases['bridei:8090'], ['ugandapartners.org','zetaweb.com'])

        self.binder.onecmd("mv zetaweb.com bridei 8080")
        self.assertEqual(self.binder.aliases['bridei:8090'], ['ugandapartners.org'])

        self.binder.onecmd("mv zetaweb.com bridei 8090")
        self.assertEqual(self.binder.aliases['bridei:8090'], ['ugandapartners.org','zetaweb.com'])

        self.binder.onecmd("mv zetaweb.com bridei 8080")
        self.assertEqual(self.binder.aliases['bridei:8090'], ['ugandapartners.org'])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCRUD))
    return suite

if __name__ == '__main__':
    unittest.main()