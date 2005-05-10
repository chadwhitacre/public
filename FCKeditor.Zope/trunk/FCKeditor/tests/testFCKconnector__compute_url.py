import os, sys, time
from pprint import pprint
import unittest

# make sure we can find ourselves
sys.path.insert(1, os.path.realpath('..'))

# the thing we want to test
from FCKeditor import FCKeditor, FCKexception
from FCKconnector import FCKconnector

def dict2tuple(d):
    """convert a dictionary to a sorted list of tuples
    """
    l = [(k, d[k]) for k in d]
    l.sort()
    return l


##
# Define our tests
##

class TestBase__compute_url(unittest.TestCase):

    def setUp(self):
        self.fck = FCKconnector()

    def testDefaultsToUserFiles(self):
        data = {}
        data['ServerPath'] = None
        data['Type'] = 'Image'
        data['CurrentFolder'] = '/Docs/Test/'

        expected = '/UserFiles/Image/Docs/Test/'
        actual = self.fck._compute_url(**data)
        self.assertEqual(actual, expected)

    def testButCanBeExplicitlyNegated(self):
        data = {}
        data['ServerPath'] = '/'
        data['Type'] = 'Image'
        data['CurrentFolder'] = '/Docs/Test/'

        expected = '/Image/Docs/Test/'
        actual = self.fck._compute_url(**data)
        self.assertEqual(actual, expected)

    def testDoesntBorkOnExtraData(self):
        data = {}
        data['ServerPath'] = '/FooBar/'
        data['Type'] = 'Image'
        data['CurrentFolder'] = '/Docs/Test/'
        data['Baz'] = 'buz'

        expected = '/FooBar/Image/Docs/Test/'
        actual = self.fck._compute_url(**data)
        self.assertEqual(actual, expected)



##
# And run them!
##

if __name__ == '__main__':
    unittest.main()
