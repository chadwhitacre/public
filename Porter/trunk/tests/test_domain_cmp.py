if __name__ == '__main__':
    import framework

import unittest
from porter.Porter import Porter, PorterError

class TestDomainCmp(unittest.TestCase):

    def setUp(self):
        self.c = Porter

    def testMinimal(self):
        domains = ['www.def.com'
                  ,'www.abc.com'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['www.abc.com'
                                  ,'www.def.com'])

    def testAllSameDepthAndTLDDiffSLDs(self):
        # only diff is SLD
        domains = ['www.zetaweb.com'
                  ,'www.thedwarf.com'
                  ,'www.malcontents.com'
                  ,'www.zetaserver.com'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['www.malcontents.com'
                                  ,'www.thedwarf.com'
                                  ,'www.zetaserver.com'
                                  ,'www.zetaweb.com'
                                   ])

    def testSameDepthDiffSLDsDiffTLDs(self):
        # no identical SLDs
        domains = ['www.zetaweb.com'
                  ,'www.thedwarf.info'
                  ,'www.malcontents.org'
                  ,'www.zetaserver.edu'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['www.malcontents.org'
                                  ,'www.thedwarf.info'
                                  ,'www.zetaserver.edu'
                                  ,'www.zetaweb.com'
                                   ])
        # should be sorted the same as previous

    def testDifferentDepthsDiffSLDsDiffTLDs(self):
        # again no identical SLDs
        domains = ['zetaweb.com'
                  ,'www.thedwarf.info'
                  ,'www.online.malcontents.org'
                  ,'online.zetaserver.edu'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['www.online.malcontents.org'
                                  ,'www.thedwarf.info'
                                  ,'online.zetaserver.edu'
                                  ,'zetaweb.com'
                                   ])
        # should be sorted the same as previous

    def testSameDepthSame3LDOverlappingTLDsDiffTLDs(self):
        # now we start introducing indetical SLDs
        domains = ['www.zetaweb.com'
                  ,'www.zetaweb.org'
                  ,'www.thedwarf.info'
                  ,'www.zetaweb.net'
                  ,'www.thedwarf.com'
                  ,'www.thedwarf.net'
                  ,'www.thedwarf.org'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['www.thedwarf.com'
                                  ,'www.thedwarf.info'
                                  ,'www.thedwarf.net'
                                  ,'www.thedwarf.org'
                                  ,'www.zetaweb.com'
                                  ,'www.zetaweb.net'
                                  ,'www.zetaweb.org'
                                   ])

    def testNoWWWFirst(self):
        domains = ['flanderous.com'
                  ,'www.flanderous.com'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['flanderous.com'
                                  ,'www.flanderous.com'
                                   ])

    def testWWWFirst(self):
        domains = ['www.flanderous.com'
                  ,'flanderous.com'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['flanderous.com'
                                  ,'www.flanderous.com'
                                   ])

    def testRecurringAgnostic(self):
        # we are not enforcing uniqueness
        # this is covered in the next test
        pass

    def testTwentyQuestions(self):
        # it looks to be working, let's throw it a curveball
        domains = ['zetaweb.com'
                  ,'www.library.tesm.us'
                  ,'www.zetaweb.org'
                  ,'thedwarf.info'
                  ,'www.online.tesm.edu'
                  ,'www.thedwarf.com'
                  ,'www.flanderous.com'
                  ,'www.library.tesm.edu'
                  ,'www.logstown.net'
                  ,'red.yellow.blue.thedwarf.com'
                  ,'flanderous.com'
                  ,'www.thedwarf.net'
                  ,'www.malcontents.info'
                  ,'library.tesm.edu'
                  ,'www.thedwarf.org'
                  ,'www.kilbyhouse.net'
                  ,'www.zetaweb.net'
                  ,'online.tesm.edu'
                  ,'www.kilbyhouse.info'
                  ,'www.thedwarf.org'
                   ]
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, ['flanderous.com'
                                  ,'www.flanderous.com'
                                  ,'www.kilbyhouse.info'
                                  ,'www.kilbyhouse.net'
                                  ,'www.logstown.net'
                                  ,'www.malcontents.info'
                                  ,'library.tesm.edu'
                                  ,'www.library.tesm.edu'
                                  ,'online.tesm.edu'
                                  ,'www.online.tesm.edu'
                                  ,'www.library.tesm.us'
                                  ,'red.yellow.blue.thedwarf.com'
                                  ,'www.thedwarf.com'
                                  ,'thedwarf.info'
                                  ,'www.thedwarf.net'
                                  ,'www.thedwarf.org'
                                  ,'www.thedwarf.org'
                                  ,'zetaweb.com'
                                  ,'www.zetaweb.net'
                                  ,'www.zetaweb.org'
                                   ])

    def testError(self):
        sort_domains = lambda d: d.sort(self.c._domain_cmp)

        domains = ['nope', "don't think so", None, 45]
        self.assertRaises(PorterError, sort_domains, domains)

        domains = ['nope',"don't think so", 'zetaweb.com']
        self.assertRaises(PorterError, sort_domains, domains)

        domains = [None,45]
        self.assertRaises(PorterError, sort_domains, domains)

        domains = []
        domains.sort(self.c._domain_cmp)
        self.assertEqual(domains, [])


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestDomainCmp))
    return suite

if __name__ == '__main__':
    unittest.main()