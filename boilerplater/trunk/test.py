#!/usr/bin/env python
#BOILERPLATE##################################################################
#                                                                             #
#  (c) 2005 Chad Whitacre <http://www.zetaweb.com/>                           #
#  This program is beerware. If you like it, buy me a beer someday.           #
#  No warranty is expressed or implied.                                       #
#                                                                             #
##################################################################BOILERPLATE#
#BOILERPLATE###################################################################
#                                                                             #
#  (c) 2005 Chad Whitacre <http://www.zetaweb.com/>                           #
#  This program is beerware. If you like it, buy me a beer someday.           #
#  No warranty is expressed or implied.                                       #
#                                                                             #
###################################################################BOILERPLATE#

import os
import sys
import unittest

from boilerplater import Boilerplater, File

class Test(unittest.TestCase):

    def datahelper(self, data):
        return '\n'.join([l.strip() for l in data.split('\n')])

    def setUp(self):
        if os.path.exists('BoilerplateMe.sh'):
            os.remove('BoilerplateMe.sh')
        testfile = file('BoilerplateMe.sh','w+')
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
        self.boilerplate = self.datahelper(data)

    def tearDown(self):
        os.remove('BoilerplateMe.sh')

    def testNoBoilerplateBoilerplateIsCreated(self):

        # If the file doesn't already have boilerplate, then an empty
        # boilerplate should be inserted on construction.

        F = File('BoilerplateMe.sh')
        expected = self.datahelper("""\
            #BOILERPLATE###################################################################
            ###################################################################BOILERPLATE#
        """)
        actual = F._boilerplate
        self.assertEqual(expected, actual)

    def testNowHasBoilerplateForReal(self):

        # After construction, the instance should now have the boilerplate
        # interpolated and this should be visible via self.read() etc.

        F = File('BoilerplateMe.sh')
        expected = self.datahelper("""\
            #!/bin/sh
            #BOILERPLATE###################################################################
            ###################################################################BOILERPLATE#

            echo 'hello world!'
        """)
        actual = F.read()
        self.assertEqual(expected, actual)

    def testBoilerplaterInsertsLicense(self):
        filepath = 'BoilerplateMe.sh'
        Boilerplater.apply_boilerplate(self.boilerplate, filepath)

        expected = self.datahelper("""\
            #BOILERPLATE###################################################################
            #                                                                             #
            #  (c) 2005 Chad Whitacre <http://www.zetaweb.com/>                           #
            #  This program is beerware. If you like it, buy me a beer someday.           #
            #  No warranty is expressed or implied.                                       #
            #                                                                             #
            ###################################################################BOILERPLATE#
        """)
        actual = File(filepath)._boilerplate
        self.assertEqual(expected, actual)

    def testBoilerplaterInsertsLicenseForReal(self):
        filepath = 'BoilerplateMe.sh'
        Boilerplater.apply_boilerplate(self.boilerplate, filepath)

        expected = self.datahelper("""\
            #!/bin/sh
            #BOILERPLATE###################################################################
            #                                                                             #
            #  (c) 2005 Chad Whitacre <http://www.zetaweb.com/>                           #
            #  This program is beerware. If you like it, buy me a beer someday.           #
            #  No warranty is expressed or implied.                                       #
            #                                                                             #
            ###################################################################BOILERPLATE#

            echo 'hello world!'
        """)
        actual = file(filepath).read()
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
