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

DATA = { 'Command'       : 'GetFolders'
       , 'ComputedUrl'   : ''
       , 'CurrentFolder' : '/'
       , 'NewFile'       : None
       , 'NewFolderName' : ''
       , 'Type'          : 'File'
       , 'ServerPath'    : ''
        }


class TestFCKconnector(unittest.TestCase):

    def setUp(self):
        self.fck = FCKconnector()

    def testGoodData(self):
        data = DATA.copy()
        data.update({ 'Command'       : 'GetFolders'
                    , 'CurrentFolder' : '/path/to/content/'
                    , 'Type'          : 'Image'
                     })
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

    def testAllCommands(self):
        data = DATA.copy()

        data['Command'] = 'GetFolders'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['Command'] = 'GetFoldersAndFiles'
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['Command'] = 'CreateFolder'
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['Command'] = 'FileUpload'
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

    def testBadCommand(self):
        data = DATA.copy()

        data['Command'] = 'YADAYADAYADA'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['Command'] = ''
        self.assertRaises(FCKexception, self.fck._validate, data)

    def testAllTypes(self):
        data = DATA.copy()

        data['Type'] = 'File'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['Type'] = 'Image'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['Type'] = 'Flash'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['Type'] = 'Media'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

    def testBadTypes(self):
        data = DATA.copy()

        data['Type'] = 'Audio'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['Type'] = ''
        self.assertRaises(FCKexception, self.fck._validate, data)

    def testCurrentFolder(self):
        data = DATA.copy()

        # must start and end with a forward slash
        data['CurrentFolder'] = '/Docs/Test/'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['CurrentFolder'] = '/'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))


        # bad data
        data['CurrentFolder'] = ''
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['CurrentFolder'] = 'Docs/Test/'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['CurrentFolder'] = '/Docs/Test'
        self.assertRaises(FCKexception, self.fck._validate, data)

    def testServerPath(self):
        data = DATA.copy()

        # must start and end with a forward slash
        data['ServerPath'] = '/Docs/Test/'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['ServerPath'] = '/'
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        data['ServerPath'] = ''
        data['ComputedUrl'] = self.fck._compute_url(**data)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(data))

        del data['ServerPath']
        expected = data.copy()
        expected['ServerPath'] = ''
        data['ComputedUrl'] = self.fck._compute_url(**expected)
        self.assertEqual( dict2tuple(self.fck._validate(data))
                        , dict2tuple(expected))


        # bad data
        data['ServerPath'] = 'Docs/Test/'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['ServerPath'] = '/Docs/Test'
        self.assertRaises(FCKexception, self.fck._validate, data)


    def test_xmlGetFolders(self):
        actual = self.fck._xmlGetFolders( Type='File'
                                        , CurrentFolder='/path/to/content/'
                                        , ComputedUrl='/'
                                        , Folders=['foo','bar']
                                         )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/" />
    <Folders>
      <Folder name="foo" />
      <Folder name="bar" />
    </Folders>
</Connector>"""
        self.assertEqual(actual, expected)

if __name__ == '__main__':
    unittest.main()
