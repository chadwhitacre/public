import os
import sys
import unittest

# make sure we can find ourselves
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# the thing we want to test
from Products.FCKeditor import FCKexception
from Products.FCKeditor.FCKconnector import FCKconnector
from Products.FCKeditor.tests import dict2tuple

##
# Define our tests
##

class TestData:

    MINIMAL = { 'Command'       : 'GetFolders'
              , 'CurrentFolder' : '/'
              , 'NewFile'       : None
              , 'NewFolderName' : ''
              , 'Type'          : 'File'
              , 'ServerPath'    : '/'
               }


class Test(unittest.TestCase):

    def setUp(self):
        self.fck = FCKconnector()

    def testMinimalDataWorks(self):
        expected = TestData.MINIMAL.copy()
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))


    # Command

    def testCommandMustMatchMethodName(self):
        expected = TestData.MINIMAL.copy()
        expected['ComputedUrl'] = self.fck._compute_url(**expected)

        expected['Command'] = 'NonExistant'
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['Command'] = ''
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['Command'] = []
        self.assertRaises(FCKexception, self.fck._validate, expected)

    def testAndOnlyTheMethodsWeAllow(self):
        expected = TestData.MINIMAL.copy()
        expected['ComputedUrl'] = self.fck._compute_url(**expected)

        expected['Command'] = '_compute_url'
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['Command'] = 'GetFolders_response'
        self.assertRaises(FCKexception, self.fck._validate, expected)

    def testAllValidCommands(self):
        expected = TestData.MINIMAL.copy()
        expected['ComputedUrl'] = self.fck._compute_url(**expected)

        expected['Command'] = 'GetFolders'
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

        expected['Command'] = 'GetFoldersAndFiles'
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

        expected['Command'] = 'CreateFolder'
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

        expected['Command'] = 'FileUpload'
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))


    # CurrentFolder

    def testCurrentFolderRoot(self):
        expected = TestData.MINIMAL.copy()

        expected['CurrentFolder'] = '/'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

    def testCurrentFolderLonger(self):
        expected = TestData.MINIMAL.copy()

        expected['CurrentFolder'] = '/Docs/Test/'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

    def testCurrentFolderNonAlpha(self):
        expected = TestData.MINIMAL.copy()

        expected['CurrentFolder'] = '/what about this?/'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

    def testCurrentFolderBadData(self):
        expected = TestData.MINIMAL.copy()

        expected['CurrentFolder'] = 'NoLeadingSlash/'
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['CurrentFolder'] = '/NoTrailingSlash'
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['CurrentFolder'] = ''
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['CurrentFolder'] = []
        self.assertRaises(AttributeError, self.fck._validate, expected)



    # NewFile and NewFolderName are optional and unvalidated



    # ServerPath

    def testServerPathGoodData(self):
        expected = TestData.MINIMAL.copy()

        # must start and end with a forward slash
        expected['ServerPath'] = '/Docs/Test/'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

        expected['ServerPath'] = '/'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

        expected['ServerPath'] = ''
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        actual = self.fck._validate(expected)
        self.assertEqual(dict2tuple(expected), dict2tuple(actual))

    def testServerPathBadData(self):
        expected = TestData.MINIMAL.copy()

        expected['ServerPath'] = 'Docs/Test/'
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['ServerPath'] = '/Docs/Test'
        self.assertRaises(FCKexception, self.fck._validate, expected)

        # ServerPath is optional, so the following doesn't trigger an error
        # until _compute_url
        expected['ServerPath'] = []
        self.assertRaises(TypeError, self.fck._validate, expected)

        # This gets caught in ServerPath validation
        expected['ServerPath'] = ['foo']
        self.assertRaises(AttributeError, self.fck._validate, expected)



    # Type

    def testAllTypes(self):
        expected = TestData.MINIMAL.copy()

        expected['Type'] = 'File'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        self.assertEqual( dict2tuple(self.fck._validate(expected))
                        , dict2tuple(expected))

        expected['Type'] = 'Image'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        self.assertEqual( dict2tuple(self.fck._validate(expected))
                        , dict2tuple(expected))

        expected['Type'] = 'Flash'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        self.assertEqual( dict2tuple(self.fck._validate(expected))
                        , dict2tuple(expected))

        expected['Type'] = 'Media'
        expected['ComputedUrl'] = self.fck._compute_url(**expected)
        self.assertEqual( dict2tuple(self.fck._validate(expected))
                        , dict2tuple(expected))

    def testBadTypes(self):
        expected = TestData.MINIMAL.copy()

        expected['Type'] = 'Audio'
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['Type'] = ''
        self.assertRaises(FCKexception, self.fck._validate, expected)

        expected['Type'] = []
        self.assertRaises(FCKexception, self.fck._validate, expected)



    # _compute_url

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

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test))
    return suite

if __name__ == '__main__':
    unittest.main()
