"""Zope-specific tests; requires ZopeTestCase
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('FCKeditor')

from AccessControl import Unauthorized
from zExceptions import BadRequest
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor
from data import testdata


##
# stub classes
##

class RESPONSE:
    def setHeader(self, *arg, **kw):
        pass

class AUTHENTICATED_USER:
    def has_permission(self, *arg, **kw):
        return True

from types import DictType
class REQUEST(DictType):

    def __init__(self, *arg, **kw):
        DictType.__init__(self, *arg, **kw)

    RESPONSE = RESPONSE()


##
# tests
##

class TestZopeFCKmanager(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        add = self.folder.manage_addProduct['FCKeditor'].manage_addFCKmanager
        add('fckmanager')
        self.fckmanager = self.folder.fckmanager

    def testInstantiateTextarea(self):
        fckeditor = self.fckmanager.spawn('MyField')
        self.assertEqual(isinstance(fckeditor, ZopeFCKeditor), True)
        fckeditor.SetCompatible(testdata.INCOMPATIBLE_USERAGENT)
        self.assertEqual(fckeditor.Create(), """\
<div>
    <textarea name="MyField"
              rows="4" cols="40"
              style="Width: 100%; Height: 200px;"
              wrap="virtual" />
"""+'        '+ # cause I trim trailing spaces in my editor
"""
    </textarea>
</div>""")

    def testInstantiateFCKeditor(self):
        fckeditor = self.fckmanager.spawn('MyField')
        self.assertEqual(isinstance(fckeditor, ZopeFCKeditor), True)
        fckeditor.SetCompatible(testdata.COMPATIBLE_USERAGENT)
        self.assertEqual(fckeditor.Create(), """\
<div>
    <input type="hidden"
           id="MyField"
           name="MyField"
           value="" />
    <input type="hidden"
           id="MyField___Config"
           value="" />
    <iframe id="MyField___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=MyField&Toolbar=Default"
            width="100%" height="200px"
            frameborder="no" scrolling="no"></iframe>
</div>""")





class TestFCKconnector(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        add = self.folder.manage_addProduct['FCKeditor'].manage_addFCKmanager
        add('fckmanager')
        self.fckmanager = self.folder.fckmanager
        self.folder.manage_addFolder('path')
        self.folder.path.manage_addFolder('to')
        self.folder.path.to.manage_addFolder('empty')
        self.folder.path.to.manage_addFolder('one')
        self.folder.path.to.one.manage_addFile('foo file')
        self.folder.path.to.manage_addFolder('content')
        self.folder.path.to.content.manage_addFolder('sub-content')
        self.folder.path.to.content.manage_addFile('foo file')
        self.folder.path.to.content.manage_addFile('bar_file')
        self.folder.path.to.content.manage_addImage('bar_image', None)


    def testEmptyFolderGetFolders(self):
        actual = self.fckmanager.GetFolders( Type = 'File'
                                           , CurrentFolder = '/path/to/empty/'
                                           , ComputedUrl = '/path/to/empty/'
                                           , User = AUTHENTICATED_USER()
                                             )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="File">
    <CurrentFolder path="/path/to/empty/" url="/path/to/empty/" />
    <Folders>
      """+"""
    </Folders>
</Connector>"""

        self.assertEqual(actual, expected)

    def testSingleItemFolderGetFolders(self):
        actual = self.fckmanager.GetFolders( Type = 'File'
                                           , CurrentFolder = '/path/to/one/'
                                           , ComputedUrl = '/path/to/one/'
                                           , User = AUTHENTICATED_USER()
                                             )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="File">
    <CurrentFolder path="/path/to/one/" url="/path/to/one/" />
    <Folders>
      """+"""
    </Folders>
</Connector>"""

        self.assertEqual(actual, expected)

    def testFolderGetFolders(self):
        actual = self.fckmanager.GetFolders( Type = 'File'
                                           , CurrentFolder = '/path/to/content/'
                                           , ComputedUrl = '/path/to/content/'
                                           , User = AUTHENTICATED_USER()
                                             )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFolders" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Folders>
      <Folder name="sub-content" />
    </Folders>
</Connector>"""

        self.assertEqual(actual, expected)

    def testFolderGetFoldersAndFiles(self):
        actual = self.fckmanager.GetFoldersAndFiles( Type = 'File'
                                                   , CurrentFolder = '/path/to/content/'
                                                   , ComputedUrl = '/path/to/content/'
                                                   , User = AUTHENTICATED_USER()
                                                    )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="GetFoldersAndFiles" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Folders>
      <Folder name="sub-content" />
    </Folders>
    <Files>
      <File name="foo file" size="0" />
      <File name="bar_file" size="0" />
    </Files>
</Connector>"""

        self.assertEqual(actual, expected)

class TestCreateFolder(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        add = self.folder.manage_addProduct['FCKeditor'].manage_addFCKmanager
        add('fckmanager')
        self.fckmanager = self.folder.fckmanager
        self.folder.manage_addFolder('path')
        self.folder.path.manage_addFolder('to')
        self.folder.path.to.manage_addFolder('content')

        self.folder.acl_users._doAddUser('admin', 'secret', ['Manager',], [])
        self.folder.acl_users._doAddUser('user1', 'secret', [], [])


    def testCreateFolder(self):
        self.login('admin')
        actual = self.fckmanager.CreateFolder( Type = 'File'
                                             , CurrentFolder = '/path/to/content/'
                                             , NewFolderName = 'foo'
                                             , ComputedUrl = '/path/to/content/'
                                              )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="0" />
</Connector>"""

        self.assertEqual(actual, expected)
        parent = self.fckmanager.path.to.content
        self.assert_(getattr(parent, 'foo', None) is not None,
                     "folder 'foo' was not created")


    def testFolderAlreadyExists(self):
        self.login('admin')
        actual = self.fckmanager.CreateFolder( Type = 'File'
                                             , CurrentFolder = '/path/to/content/'
                                             , NewFolderName = 'foo'
                                             , ComputedUrl = '/path/to/content/'
                                              )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="0" />
</Connector>"""

        self.assertEqual(actual, expected)
        parent = self.fckmanager.path.to.content
        self.assert_(getattr(parent, 'foo', None) is not None,
                     "folder 'foo' was not created")

        actual = self.fckmanager.CreateFolder( Type = 'File'
                                             , CurrentFolder = '/path/to/content/'
                                             , NewFolderName = 'foo'
                                             , ComputedUrl = '/path/to/content/'
                                              )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="101" />
</Connector>"""

        self.assertEqual(actual, expected)


    def testCanOverrideParentNames(self):
        self.login('admin')
        actual = self.fckmanager.CreateFolder( Type = 'File'
                                             , CurrentFolder = '/path/to/content/'
                                             , NewFolderName = 'to'
                                             , ComputedUrl = '/path/to/content/'
                                              )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="0" />
</Connector>"""

        self.assertEqual(actual, expected)
        parent = self.fckmanager.path.to.content
        self.assert_(getattr(parent, 'to', None) is not None,
                     "folder 'to' was not created")


    def testCreatFolderBadName(self):
        self.login('admin')
        actual = self.fckmanager.CreateFolder( Type = 'File'
                                             , CurrentFolder = '/path/to/content/'
                                             , NewFolderName = '_JAR!JAR!'
                                             , ComputedUrl = '/path/to/content/'
                                              )
        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="102" />
</Connector>"""

        self.assertEqual(actual, expected)
        parent = self.fckmanager.path.to.content
        self.assert_(getattr(parent, '_JAR!JAR!', None) is None,
                     "folder '_JAR!JAR!' was created")



    def testCreateFolderPermissions(self):

        # the connector itself is public, security is delegated to the methods
        connector = self.folder.restrictedTraverse('fckmanager/connector')


        ##
        # anonymous
        ##
        self.logout()
        req = REQUEST({ 'Command'       : 'CreateFolder'
                      , 'Type'          : 'File'
                      , 'CurrentFolder' : '/path/to/content/'
                      , 'NewFolderName' : 'foo'
                       })
        actual = connector(req)

        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="103" />
</Connector>"""

        self.assertEqual(actual, expected)


        ##
        # bare authenticated
        ##
        self.login('user1')
        req = REQUEST({ 'Command'       : 'CreateFolder'
                      , 'Type'          : 'File'
                      , 'CurrentFolder' : '/path/to/content/'
                      , 'NewFolderName' : 'foo'
                      , 'AUTHENTICATED_USER' : AUTHENTICATED_USER()
                       })
        actual = connector(req)

        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="103" />
</Connector>"""

        self.assertEqual(actual, expected)


        ##
        # manager -- should succeed
        ##
        self.login('admin')
        req = REQUEST({ 'Command'       : 'CreateFolder'
                      , 'Type'          : 'File'
                      , 'CurrentFolder' : '/path/to/content/'
                      , 'NewFolderName' : 'foo'
                       })
        actual = connector(req)

        expected = """\
<?xml version="1.0" encoding="utf-8" ?>
  <Connector command="CreateFolder" resourceType="File">
    <CurrentFolder path="/path/to/content/" url="/path/to/content/" />
    <Error number="0" />
</Connector>"""

        self.assertEqual(actual, expected)



##
# Assemble into a suite and run
##

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZopeFCKeditor))
    suite.addTest(makeSuite(TestZopeFCKmanager))
    suite.addTest(makeSuite(TestFCKconnector))
    suite.addTest(makeSuite(TestCreateFolder))
    return suite

if __name__ == '__main__':
    framework()
