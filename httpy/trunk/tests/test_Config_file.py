#!/usr/bin/env python

import os
import unittest
from ConfigParser import ParsingError

from ConfigurationTestCase import ConfigurationTestCase


default_conf = """\
[server]
ip =
port = 8080

[handler]
root = .
defaults = index.html index.pt
extensions = pt
mode = deployment
"""

no_header = """\
ip =
port = 8080
root = .
defaults = index.html index.pt
extensions = pt
mode = deployment
"""

one_option = """\
[server]
port = 8080

[network]
"""

one_header = """\
[default]
ip =
port = 8080
root = .
defaults = index.html index.pt
extensions = pt
mode = deployment
"""

meaningless_headers = """\
[I like]
ip =
port = 8080

[cheese.]
root = .
defaults = index.html index.pt
extensions = pt
mode = deployment
"""

wacky_headers = """\
[The IP Address]
ip =
[The TCP Port]
port = 8080
[The Publishing Root]
root = .
[The Default Documents]
defaults = index.html index.pt
[The Page Template File Extensions]
extensions = pt
[The Server Mode]
mode = deployment
"""

extra_options = """\
[server]
ip =
port = 8080
cheese = yummy

[handler]
root = .
defaults = index.html index.pt
extensions = pt
mode = deployment
"""

class TestConfigurationFile(ConfigurationTestCase):

    d = {}
    d['ip'] = ''
    d['port'] = 8080
    d['root'] = os.path.realpath('.')
    d['defaults'] = ('index.html', 'index.pt')
    d['extensions'] = ('pt',)
    d['mode'] = 'deployment'

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

    def testButTheNamesOfTheSectionHeadersDoesntMatter(self):
        conf = open('httpy.conf', 'w')
        conf.write(meaningless_headers)
        conf.close()
        expected = self.dict2tuple(self.d.copy())
        actual = self.dict2tuple(self.config._file('httpy.conf'))
        self.assertEqual(expected, actual)

    def testInFactTheOptionsCanAllBeInOneSection(self):
        conf = open('httpy.conf', 'w')
        conf.write(one_header)
        conf.close()
        expected = self.dict2tuple(self.d.copy())
        actual = self.dict2tuple(self.config._file('httpy.conf'))
        self.assertEqual(expected, actual)

    def testOrEachInTheirOwnSection(self):
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
    suite.addTest(makeSuite(TestConfigurationFile))
    return suite

if __name__ == '__main__':
    unittest.main()
