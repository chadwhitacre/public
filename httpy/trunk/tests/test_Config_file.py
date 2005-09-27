#!/usr/bin/env python

import os
import unittest
from ServerConfigParser import ParsingError

from TestCaseHttpy import TestCaseHttpy


default_conf = """\
[main]
ip =
port = 8080
mode = deployment
root = .
apps =
verbosity = 1
"""

no_header = """\
ip =
port = 8080
mode = deployment
root = .
apps =
verbosity = 1
"""

one_option = """\
[main]
port = 8080
"""

meaningless_header = """\
[CHEESE!!!!!!!!!!1]
ip =
port = 8080
mode = deployment
root = .
apps =
verbosity = 1
"""

wacky_headers = """\
[The IP Address]
ip =
[The TCP Port]
port = 8080
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
ip =
port = 8080
cheese = yummy
mode = deployment
root = .
apps =
verbosity = 1
"""

class TestServerConfigFile(TestCaseHttpy):

    d = {}
    d['ip'] = ''
    d['port'] = 8080
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
        expected = self.dict2tuple({'port':8080})
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

    def testAndMultipleHeadersDoesntMatter(self):
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
    suite.addTest(makeSuite(TestServerConfigFile))
    return suite

if __name__ == '__main__':
    unittest.main()
