#!/usr/bin/env python

import os
import unittest

from kraken.Kraken import Kraken



dummy_config = """\
[imap]
username    = mylist@example.com
password    = foobar
server      = imap.example.com
port        = 143

[smtp]
username    = mylist@example.com
password    = foobar
server      = smtp.example.com
port        = 25
"""

addrs1 = [ 'chad@zetaweb.com']
addrs1 = os.linesep.join(addrs1)

addrs2 = [ 'chad@zetaweb.com'
         , 'whit537@gmail.com'
         , 'info@zetaweb.com'
          ]
addrs2 = os.linesep.join(addrs2)


class KrakenTestCase(unittest.TestCase):

    def setUp(self):
        self.removeWhale()
        os.mkdir('whale')
        file('whale/config','w').write(dummy_config)
        file('whale/to.addrs','w').write(addrs1)
        file('whale/from.addrs','w').write(addrs2)

        self.kraken = Kraken('whale')
        self.whale = self.kraken.whale


    def tearDown(self):
        self.removeWhale()

    def removeWhale(self):
        if not os.path.isdir('whale'):
            return
        for root, dirs, files in os.walk('whale', topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('whale')
