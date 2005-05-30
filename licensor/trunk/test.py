#!/usr/bin/env python

import os
import sys
import unittest

from licensor import Licensor, Licensee

class Test(unittest.TestCase):

    def datahelper(self, data):
        return '\n'.join([l.strip() for l in data.split('\n')])

    def setUp(self):
        if os.path.exists('LicenseMe.sh'):
            os.remove('LicenseMe.sh')
        testfile = file('LicenseMe.sh','w+')
        data = """\
            #!/bin/sh

            echo 'hello world!'
        """
        testfile.write(self.datahelper(data))
        testfile.close()

        data = """\
            (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
            This program is beerware. If you like it, buy me a beer someday.
            No warranty is expressed or implied."""
        self.license = self.datahelper(data)

    def tearDown(self):
        os.remove('LicenseMe.sh')

    def testNoLicenseLicenseIsCreated(self):

        # If the file doesn't already have a license, then an empty license
        # should be inserted on construction.

        l = Licensee('LicenseMe.sh')
        expected = self.datahelper("""\
            #LICENSOR######################################################################
            ######################################################################LICENSOR#
        """)
        actual = l._license
        self.assertEqual(expected, actual)

    def testNowHasLicenseForReal(self):

        # After construction, the instance should now have the license
        # interpolated and this should be visible via self.read() etc.

        l = Licensee('LicenseMe.sh')
        expected = self.datahelper("""\
            #!/bin/sh
            #LICENSOR######################################################################
            ######################################################################LICENSOR#

            echo 'hello world!'
        """)
        actual = l.read()
        self.assertEqual(expected, actual)

    def testLicensorInsertsLicense(self):
        licensor = Licensor()
        l = Licensee('LicenseMe.sh')
        licensor.license(self.license, l)

        expected = self.datahelper("""\
            #LICENSOR######################################################################
            #                                                                             #
            #  (c) 2005 Chad Whitacre <http://www.zetaweb.com/>                           #
            #  This program is beerware. If you like it, buy me a beer someday.           #
            #  No warranty is expressed or implied.                                       #
            #                                                                             #
            ######################################################################LICENSOR#
        """)
        actual = l._license
        self.assertEqual(expected, actual)

    def testLicensorInsertsLicenseForReal(self):
        licensor = Licensor()
        l = Licensee('LicenseMe.sh')
        licensor.license(self.license, l)

        expected = self.datahelper("""\
            #!/bin/sh
            #LICENSOR######################################################################
            #                                                                             #
            #  (c) 2005 Chad Whitacre <http://www.zetaweb.com/>                           #
            #  This program is beerware. If you like it, buy me a beer someday.           #
            #  No warranty is expressed or implied.                                       #
            #                                                                             #
            ######################################################################LICENSOR#

            echo 'hello world!'
        """)
        actual = l.read()
        self.assertEqual(expected, actual)

class Test2(unittest.TestCase):

    def datahelper(self, data):
        return '\n'.join([l.strip() for l in data.split('\n')])

    def setUp(self):
        if os.path.exists('LicenseMe.sh'):
            os.remove('LicenseMe.sh')
        testfile = file('LicenseMe.sh','w+')
        data = """\
            #!/bin/sh

            echo 'hello world!'
        """
        testfile.write(self.datahelper(data))
        testfile.close()

        data = """\
            (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
            This program is beerware. If you like it, buy me a beer someday.
            No warranty is expressed or implied."""
        self.license = self.datahelper(data)

    def tearDown(self):
        os.remove('LicenseMe.sh')

    def testNoLicenseLicenseIsCreated(self):

        # If the file doesn't already have a license, then an empty license
        # should be inserted on construction.


if __name__ == '__main__':
    unittest.main()
