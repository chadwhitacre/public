import unittest, os, pdb
from StringIO import StringIO
from porter.PorterCmd import PorterCmd

class TestCRUD(unittest.TestCase):

    def setUp(self):
        self.out = StringIO()
        try: os.remove('test_db.db')
        except: pass
        self.c = PorterCmd('test_db', stdout=self.out)

    def tearDown(self):
        os.remove('test_db.db')

    def testListWhenEmpty(self):
        self.c.onecmd("ls")
        self.assertEqual(self.out.getvalue(), '')

    def testBadInput(self):
        self.c.onecmd("add test")
        self.assertEqual(self.out.getvalue(), "We need a domain name and a" +\
                                              " website id.\n")

    def testAddOneItem(self):
        self.c.onecmd("add zetaweb.com abondance@alpin:8010")
        self.c.onecmd("ls")
        self.assertEqual(self.c.domains, {'zetaweb.com':'abondance@alpin:8010'})
        self.assertEqual(self.c.websites, {'abondance@alpin:8010':['zetaweb.com']})
        self.assertEqual(self.out.getvalue(), 'zetaweb.com\n')

    def testExtraInputIsIgnored(self):
        self.c.onecmd("add test test Frank Sinatra sings the blues")
        self.assertEqual(self.c.domains, {"test":"test"})

    def testAddMultipleItems(self):
        self.c.onecmd("add zetaweb.com abondance@alpin:8010")
        self.c.onecmd("map thedwarf.com caithness@duder:8020")
        self.c.onecmd("edit malcontents.org caithness@duder:8020")
        self.c.onecmd("map christyanity.com caithness@duder:8020")
        self.c.onecmd("add tesm.edu asiago@underbird:8310")

        domains = self.c.domains.keys(); domains.sort()
        self.assertEqual(domains, ['christyanity.com'
                                  ,'malcontents.org'
                                  ,'tesm.edu'
                                  ,'thedwarf.com'
                                  ,'zetaweb.com'
                                   ])

        websites = self.c.websites.keys(); websites.sort()
        self.assertEqual(websites, ['abondance@alpin:8010'
                                   ,'asiago@underbird:8310'
                                   ,'caithness@duder:8020'
                                     ])

        multi_domains = self.c.websites['caithness@duder:8020']
        multi_domains.sort()
        self.assertEqual(multi_domains, ['christyanity.com'
                                        ,'malcontents.org'
                                        ,'thedwarf.com'
                                         ])

        single_domain = self.c.websites['abondance@alpin:8010']
        self.assertEqual(single_domain, ['zetaweb.com'])

        single_domain = self.c.websites['asiago@underbird:8310']
        self.assertEqual(single_domain, ['tesm.edu'])

    def testList(self):
        self.c.onecmd("add zetaweb.com abondance@alpin:8010")
        self.c.onecmd("map thedwarf.com caithness@duder:8020")
        self.c.onecmd("edit malcontents.org caithness@duder:8020")
        self.c.onecmd("map christyanity.com caithness@duder:8020")
        self.c.onecmd("add tesm.edu asiago@underbird:8310")
        self.c.onecmd("add zoobaz.info dummy")
        self.c.onecmd("add latebutlaughing.com dummy")

        expected = """\
christyanity.com     malcontents.org  thedwarf.com  zoobaz.info
latebutlaughing.com  tesm.edu         zetaweb.com \n"""

        self.c.onecmd("list")
        self.assertEqual(self.out.getvalue(), expected)

        # clear out our output
        self.out = StringIO()
        self.c.stdout = self.out

        # test our alias
        self.c.onecmd("ls")
        self.assertEqual(self.out.getvalue(), expected)

    def testRemove(self):
        self.c.onecmd("add zetaweb.com abondance@alpin:8010")
        self.c.onecmd("map thedwarf.com caithness@duder:8020")
        self.c.onecmd("edit malcontents.org caithness@duder:8020")
        self.c.onecmd("map christyanity.com caithness@duder:8020")
        self.c.onecmd("add tesm.edu asiago@underbird:8310")
        self.c.onecmd("add zoobaz.info dummy")
        self.c.onecmd("add latebutlaughing.com dummy")

        self.c.onecmd("remove zetaweb.com")
        self.assertEqual(len(self.c.domains), 6)
        self.assert_('zetaweb.com' not in self.c.domains)
        domains = []
        for w in self.c.websites:
            domains += self.c.websites[w]
        self.assertEqual(len(domains), 6)
        self.assert_('zetaweb.com' not in domains)

        self.c.onecmd("remove thedwarf.com malcontents.org christyanity.com")
        self.assertEqual(len(self.c.domains), 3)
        self.assert_('thedwarf.com' not in self.c.domains)
        self.assert_('malcontents.org' not in self.c.domains)
        self.assert_('christyanity.com' not in self.c.domains)
        domains = []
        for w in self.c.websites:
            domains += self.c.websites[w]
        self.assertEqual(len(domains), 3)
        self.assert_('thedwarf.com' not in domains)
        self.assert_('malcontents.org' not in domains)
        self.assert_('christyanity.com' not in domains)

        self.c.onecmd("rm latebutlaughing.com")
        self.assertEqual(len(self.c.domains), 2)
        self.assert_('latebutlaughing.com' not in self.c.domains)
        domains = []
        for w in self.c.websites:
            domains += self.c.websites[w]
        self.assertEqual(len(domains), 2)
        self.assert_('latebutlaughing.com' not in domains)

        domains = self.c.domains.keys(); domains.sort()
        self.assertEqual(domains, ['tesm.edu','zoobaz.info'])


if __name__ == '__main__':
    unittest.main()