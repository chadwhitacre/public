"""Zope-specific tests; requires ZopeTestCase
"""

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('FCKeditor')

from zExceptions import BadRequest
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor
from data import testdata

class TestZopeFCKeditor(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        self.add = self.folder.manage_addProduct['FCKeditor'].manage_addFCKeditor
        self.add('fck')
        self.fck = self.folder.fck

    def testSomething(self):
        self.failUnless(hasattr(self, 'fck'),
                        "FCKeditor was not installed")
        self.failUnless(isinstance(self.fck, ZopeFCKeditor),
                        "FCKeditor was not installed properly")

    def testInstanceNameScrubber(self):
        self.assertEqual(self.fck.InstanceName, 'fck')

        # Zope does do some ID validation -- [^a-zA-Z0-9-_~,.$\(\)# ]
        self.assertRaises( BadRequest, self.add
                         , "123-456fck2_oh yeah, believe-it!!!!BABY!!!!!!!~@#$%$#!)'(*@PO#JTKHEE.")

        # But CSS identifier rules are even stricter -- [^a-zA-Z0-9-]
        SAFE_FOR_ZOPE = "123-456fck2_oh yeah, believe-itBABY~#$$#)(PO#JTKHEE."
        SAFE_FOR_CSS  = "fck2-oh-yeah--believe-itBABY-------PO-JTKHEE-"
        self.add(SAFE_FOR_ZOPE)
        self.assertEqual(hasattr(self.folder, SAFE_FOR_ZOPE), True)
        self.assertEqual(getattr(self.folder, SAFE_FOR_ZOPE).InstanceName
                        , SAFE_FOR_CSS )


class TestZopeFCKmanager(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        add = self.folder.manage_addProduct['FCKeditor'].manage_addFCKmanager
        add('fckmanager')
        self.fckmanager = self.folder.fckmanager

    def testCanAddOtherObjectsProgrammatically(self):
        # afaict we in fact can't constrain programmatic addition of objects
        self.fckmanager.manage_addProduct['OFSP'].manage_addFolder('foo')
        self.assertEqual(hasattr(self.fckmanager, 'foo'), True)

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
        #self.folder.path.to.content.manage_addFolder('sub-content')
        #self.folder.path.to.content.manage_addFolder('sub-content')


    def testEmptyFolderGetFolders(self):
        actual = self.fckmanager.GetFolders( Type = 'File'
                                           , CurrentFolder = '/path/to/empty/'
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

##
# Assemble into a suite and run
##

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZopeFCKeditor))
    suite.addTest(makeSuite(TestZopeFCKmanager))
    suite.addTest(makeSuite(TestFCKconnector))
    return suite

if __name__ == '__main__':
    framework()
