import os
import sys
import unittest

# make sure we can find ourselves
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# the thing we want to test
from Products.FCKeditor import FCKexception
from Products.FCKeditor.FCKconnector import FCKconnector

##
# Define our tests
##

class TestData:

    GetFolders = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="File">
    <CurrentFolder path="/Docs/Test/" url="/" />
    <Folders>
      <Folder name="foo" />
      <Folder name="bar" />
    </Folders>
</Connector>"""

    GetFoldersEmpty = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="File">
    <CurrentFolder path="/Docs/Test/" url="/" />
    <Folders>
      """+"""
    </Folders>
</Connector>"""

    GetFoldersAndFiles = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFoldersAndFiles" resourceType="File">
    <CurrentFolder path="/Docs/Test/" url="/" />
    <Folders>
      <Folder name="foo" />
      <Folder name="bar" />
    </Folders>
    <Files>
      <File name="baz" size="200" />
      <File name="buz" size="1024" />
      <File name="boz" size="0" />
    </Files>
</Connector>"""

    CreateFolder = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/Docs/Test/" url="/" />
    <Error number="404" />
</Connector>"""

    FileUpload = """\
<script type="text/javascript">
    window.parent.frames['frmUpload'].OnUploadCompleted(404) ;
</script>"""

class Test(unittest.TestCase):

    def setUp(self):
        self.fck = FCKconnector()

    def testGetFolders_response(self):
        expected = TestData.GetFolders
        actual = self.fck.GetFolders_response( Type = 'File'
                                             , CurrentFolder = '/Docs/Test/'
                                             , ComputedUrl = '/'
                                             , folders = ['foo', 'bar'])
        self.assertEqual(actual, expected)

    def testGetFoldersNoFolders(self):
        expected = TestData.GetFoldersEmpty
        actual = self.fck.GetFolders_response( Type = 'File'
                                             , CurrentFolder = '/Docs/Test/'
                                             , ComputedUrl = '/'
                                             , folders = [])
        self.assertEqual(actual, expected)

    def testGetFoldersAndFiles_response(self):
        expected = TestData.GetFoldersAndFiles
        actual = self.fck.GetFoldersAndFiles_response(
                                               Type = 'File'
                                             , CurrentFolder = '/Docs/Test/'
                                             , ComputedUrl = '/'
                                             , folders = ['foo', 'bar']
                                             , files = [('baz', 200)
                                                       ,('buz', '1024')
                                                       ,('boz', 0)]
                                              )
        self.assertEqual(actual, expected)

    def testCreateFolder_response(self):
        expected = TestData.CreateFolder
        actual = self.fck.CreateFolder_response( Type = 'File'
                                               , CurrentFolder = '/Docs/Test/'
                                               , ComputedUrl = '/'
                                               , error_code = 404
                                                )
        self.assertEqual(actual, expected)

    def testFileUpload_response(self):
        expected = TestData.FileUpload
        actual = self.fck.FileUpload_response(param_string = 404)
        self.assertEqual(actual, expected)



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
