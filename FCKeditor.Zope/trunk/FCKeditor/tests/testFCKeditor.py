import os, sys, time
from pprint import pprint
import unittest

# make sure we can find ourselves
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


# the thing we want to test
from Products.FCKeditor.FCKeditor import FCKeditor


##
# Define our tests
##

class TestFCKeditor(unittest.TestCase):

    def setUp(self):
        self.fck = FCKeditor()

    def testInstantiation(self):
        self.failUnless( isinstance(self.fck, FCKeditor)
                       , "error instantiating FCKeditor"
                       )

    def testSimpleConfig(self):
        self.fck.set_config('AutoDetectLanguage','false')
        self.fck.set_config('DefaultLanguage','pt-BR')
        qs = self.fck.get_config_querystring()
        self.failUnlessEqual(qs, "AutoDetectLanguage=false&DefaultLanguage=pt-BR")

    def testUrlEncodedConfig(self):
        self.fck.config = {} # hmmm ... not sure why I need this
        self.fck.set_config('foo','&I need:  "URL encoding"')
        self.fck.set_config('so do *I*','bar')
        qs = self.fck.get_config_querystring()
        self.failUnlessEqual(qs,"foo=%26I+need%3A++%22URL+encoding%22" +\
                                 "&so+do+%2AI%2A=bar")



if __name__ == '__main__':
    unittest.main()

