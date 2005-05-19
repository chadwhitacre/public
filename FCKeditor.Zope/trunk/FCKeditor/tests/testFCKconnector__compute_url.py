import os
import sys
import unittest

# make sure we can find ourselves
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# the thing we want to test
from Products.FCKeditor.FCKconnector import FCKconnector

##
# Define our tests
##

class Test(unittest.TestCase):

    def setUp(self):
        self.fck = FCKconnector()

    def testDefaultsToUserFiles(self):
        data = {}
        data['ServerPath'] = None
        data['Type'] = 'Image'
        data['CurrentFolder'] = '/Docs/Test/'

        expected = '/UserFiles/Image/Docs/Test/'
        actual = self.fck._compute_url(**data)
        self.assertEqual(expected, actual)

    def testButCanBeExplicitlyNegated(self):
        data = {}
        data['ServerPath'] = '/'
        data['Type'] = 'Image'
        data['CurrentFolder'] = '/Docs/Test/'

        expected = '/Image/Docs/Test/'
        actual = self.fck._compute_url(**data)
        self.assertEqual(expected, actual)

    def testDoesntBorkOnExtraData(self):
        data = {}
        data['ServerPath'] = '/FooBar/'
        data['Type'] = 'Image'
        data['CurrentFolder'] = '/Docs/Test/'
        data['Baz'] = 'buz'

        expected = '/FooBar/Image/Docs/Test/'
        actual = self.fck._compute_url(**data)
        self.assertEqual(expected, actual)



##
# And run them!
##

if __name__ == '__main__':
    unittest.main()
