import unittest, os, pdb
from StringIO import StringIO
from porter.Porter import Porter

class TestCRUD(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()
        try: os.remove('test_db.db')
        except: pass
        self.c = Porter('test_db', stdout=self.out)

    def tearDown(self):
        os.remove('test_db.db')

    def testListWhenEmpty(self):
        self.c.onecmd("ls")
        self.assertEqual(self.out.getvalue(), '')

    def testBadInput(self):
        self.c.onecmd("add test")
        self.assertEqual(self.out.getvalue(), "We need a domain name, a " +\
                                              "server name, and a port " +\
                                              "number.\n")

    def testAddOneItem(self):
        self.c.onecmd("add zetaweb.com alpin 8010")
        self.c.onecmd("ls")
        self.assertEqual(self.c.domains, {'zetaweb.com':'alpin:8010'})
        self.assertEqual(self.c.aliases, {'alpin:8010':['zetaweb.com']})
        self.assertEqual(self.out.getvalue(), 'zetaweb.com\n')

    def testExtraInputIsIgnored(self):
        self.c.onecmd("add domain server port Frank Sinatra sings the blues")
        self.assertEqual(self.c.domains, {"domain":"server:port"})

    def testAddMultipleItems(self):
        self.c.onecmd("add zetaweb.com alpin 8010")
        self.c.onecmd("map thedwarf.com duder 8020")
        self.c.onecmd("add malcontents.org duder 8020")
        self.c.onecmd("map christyanity.com duder 8020")
        self.c.onecmd("add tesm.edu underbird 8310")

        domains = self.c.domains.keys(); domains.sort()
        self.assertEqual(domains, ['christyanity.com'
                                  ,'malcontents.org'
                                  ,'tesm.edu'
                                  ,'thedwarf.com'
                                  ,'zetaweb.com'
                                   ])

        aliases = self.c.aliases.keys(); aliases.sort()
        self.assertEqual(aliases, ['alpin:8010'
                                  ,'duder:8020'
                                  ,'underbird:8310'
                                   ])

        multi_domains = self.c.aliases['duder:8020']
        multi_domains.sort()
        self.assertEqual(multi_domains, ['christyanity.com'
                                        ,'malcontents.org'
                                        ,'thedwarf.com'
                                         ])

        single_domain = self.c.aliases['alpin:8010']
        self.assertEqual(single_domain, ['zetaweb.com'])

        single_domain = self.c.aliases['underbird:8310']
        self.assertEqual(single_domain, ['tesm.edu'])

    def testList(self):
        self.c.onecmd("add zetaweb.com alpin 8010")
        self.c.onecmd("map thedwarf.com duder 8020")
        self.c.onecmd("add malcontents.org duder 8020")
        self.c.onecmd("map christyanity.com duder 8020")
        self.c.onecmd("add tesm.edu underbird 8310")
        self.c.onecmd("add zoobaz.info dummy 80")
        self.c.onecmd("add latebutlaughing.com dummy 80")

        expected = """\
christyanity.com     malcontents.org  thedwarf.com  zoobaz.info
latebutlaughing.com  tesm.edu         zetaweb.com \n"""

        self.c.onecmd("ls")
        self.assertEqual(self.out.getvalue(), expected)

    def testRemove(self):
        self.c.onecmd("add zetaweb.com alpin 8010")
        self.c.onecmd("map thedwarf.com duder 8020")
        self.c.onecmd("add malcontents.org duder 8020")
        self.c.onecmd("map christyanity.com duder 8020")
        self.c.onecmd("add tesm.edu underbird 8310")
        self.c.onecmd("add zoobaz.info dummy 80")
        self.c.onecmd("add latebutlaughing.com dummy 80")

        self.c.onecmd("rm zetaweb.com")
        self.assertEqual(len(self.c.domains), 6)
        self.assert_('zetaweb.com' not in self.c.domains)
        domains = []
        for w in self.c.aliases:
            domains += self.c.aliases[w]
        self.assertEqual(len(domains), 6)
        self.assert_('zetaweb.com' not in domains)

        self.c.onecmd("rm thedwarf.com malcontents.org christyanity.com")
        self.assertEqual(len(self.c.domains), 3)
        self.assert_('thedwarf.com' not in self.c.domains)
        self.assert_('malcontents.org' not in self.c.domains)
        self.assert_('christyanity.com' not in self.c.domains)
        domains = []
        for w in self.c.aliases:
            domains += self.c.aliases[w]
        self.assertEqual(len(domains), 3)
        self.assert_('thedwarf.com' not in domains)
        self.assert_('malcontents.org' not in domains)
        self.assert_('christyanity.com' not in domains)

        self.c.onecmd("rm latebutlaughing.com")
        self.assertEqual(len(self.c.domains), 2)
        self.assert_('latebutlaughing.com' not in self.c.domains)
        domains = []
        for w in self.c.aliases:
            domains += self.c.aliases[w]
        self.assertEqual(len(domains), 2)
        self.assert_('latebutlaughing.com' not in domains)

        domains = self.c.domains.keys(); domains.sort()
        self.assertEqual(domains, ['tesm.edu','zoobaz.info'])


if __name__ == '__main__':
    unittest.main()