#!/usr/bin/env python

import os
import unittest
from ConfigParser import ParsingError

from TestCaseHttpy import TestCaseHttpy


default_conf = """\
[main]
sockfam = AF_INET
address = :8080
mode = deployment
root = .
apps =
verbosity = 1
"""

no_header = """\
sockfam = AF_INET
address = :8080
mode = deployment
root = .
apps =
verbosity = 1
"""

one_option = """\
[main]
address = :8080
"""

meaningless_header = """\
[CHEESE!!!!!!!!!!1]
sockfam = AF_INET
address = :8080
mode = deployment
root = .
apps =
verbosity = 1
"""

wacky_headers = """\
[The IP Address]
sockfam = AF_INET
[The TCP Port]
address = :8080
[The Server Mode]
mode = deployment
[The Publishing Root]
root = .
[The Application Paths]
apps =
[The Verbosity Level]
verbosity = 1
"""

extra_options = """\
[main]
sockfam = AF_INET
address = :8080
cheese = yummy
mode = deployment
root = .
apps =
verbosity = 1
"""

class TestConfigFile(TestCaseHttpy):

    want_config = True

    d = {}
    d['sockfam'] = 2 # socket.AF_INET
    d['address'] = ':8080' # no validation/coercion yet!
    d['mode'] = 'deployment'
    d['root'] = os.path.realpath('.')
    d['apps'] = ()
    d['verbosity'] = 1

    def testDefaultsAsFile(self):
        conf = open('httpy.conf', 'w')
        conf.write(default_conf)
        conf.close()
        expected = self.dict2tuple(self.d.copy())
        actual = self.dict2tuple(self.config._file('httpy.conf'))
        self.assertEqual(expected, actual)

    def testOnlyOneFromFile(self):
        conf = open('httpy.conf', 'w')
        conf.write(one_option)
        conf.close()
        expected = self.dict2tuple({'address':':8080'})
        actual = self.dict2tuple(self.config._file('httpy.conf'))
        self.assertEqual(expected, actual)

    def testMustHaveSectionHeader(self):
        conf = open('httpy.conf', 'w')
        conf.write(no_header)
        conf.close()
        self.assertRaises( ParsingError
                         , self.config._file
                         , 'httpy.conf'
                          )

    def testButTheNamesOfTheSectionHeaderDoesntMatter(self):
        conf = open('httpy.conf', 'w')
        conf.write(meaningless_header)
        conf.close()
        expected = self.dict2tuple(self.d.copy())
        actual = self.dict2tuple(self.config._file('httpy.conf'))
        self.assertEqual(expected, actual)

    def testAndMultsockfamleHeadersDoesntMatter(self):
        conf = open('httpy.conf', 'w')
        conf.write(wacky_headers)
        conf.close()
        expected = self.dict2tuple(self.d.copy())
        actual = self.dict2tuple(self.config._file('httpy.conf'))
        self.assertEqual(expected, actual)

    def testExtraOptionsAreIgnored(self):
        conf = open('httpy.conf', 'w')
        conf.write(extra_options)
        conf.close()
        expected = self.dict2tuple(self.d.copy())
        actual = self.dict2tuple(self.config._file('httpy.conf'))
        self.assertEqual(expected, actual)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestConfigFile))
    return suite

if __name__ == '__main__':
    unittest.main()
