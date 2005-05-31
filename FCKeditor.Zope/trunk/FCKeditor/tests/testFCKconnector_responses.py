#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre < http://www.zetadev.com/ >               #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
#                                                                             #
###################################################################BOILERPLATE#
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
