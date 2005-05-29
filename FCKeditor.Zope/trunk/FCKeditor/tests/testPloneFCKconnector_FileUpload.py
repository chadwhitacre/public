# make sure we can find ourselves
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Zope/Plone
from Testing import ZopeTestCase
from Products.CMFPlone.tests import PloneTestCase
from ZPublisher.HTTPRequest import FileUpload as ZopeFileUpload
#from Products.PageTemplates.tests.testZopePageTemplate import DummyFileUpload
from cgi import FieldStorage

# us
from Products.FCKeditor.tests import dict2tuple as d2t
from Products.FCKeditor.PloneFCKconnector import PloneFCKconnector


##
# Tweak the test fixture
##

ZopeTestCase.installProduct('FCKeditor')


##
# Define our tests
##

class DummyFileUpload(file):
    filename = ''
    headers = {'content-type':'application/octet-stream'} # whatever
    def __init__(self, filename):
        self.filename = filename
        file.__init__(self, 'blank.pdf')
    def __repr__(self):
        return "<DummyFileUpload named '%s'>" % self.filename


class Test(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.portal.portal_quickinstaller.installProduct('FCKeditor')
        self.fckc = self.portal.portal_fckconnector

        self.portal.acl_users._doAddUser('admin', 'secret', ['Manager'], [])
        self.portal.acl_users._doAddUser('user', 'secret', ['Member'], [])

        self.login('admin')
        self.portal.invokeFactory('Folder', 'Docs')
        self.logout()

    def testCurrentFolderDoesntExist(self):
        Type = ''
        CurrentFolder = '/Nonexistant/'
        NewFile = DummyFileUpload('blank.pdf')

        expected = {'param_string': '202'}
        actual = self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.assertEqual(d2t(expected), d2t(actual))

        # but only KeyErrors are caught
        CurrentFolder = []
        self.assertRaises( TypeError, self.fckc.FileUpload, Type
                         , CurrentFolder, NewFile
                          )

    # the rest assume the folder exists


    def testUserDoesntHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        NewFile = DummyFileUpload('blank.pdf')

        expected = {'param_string': '202'}
        self.login('user')
        actual = self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()
        self.assertEqual(d2t(expected), d2t(actual))

    def testUserDoesHavePermission(self):
        Type = ''
        CurrentFolder = '/'
        NewFile = DummyFileUpload('blank.pdf')

        expected = {'param_string': '0'}
        self.login('admin')
        actual = self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()
        self.assertEqual(d2t(expected), d2t(actual))

    # the rest assume the user has permission on the folder in question


    # The name collision tests would properly be in testFCKconnector.py, since
    # this functionality has been factored out into a method of FCKconnector.

    def testBasicNameCollision(self):
        Type = ''
        CurrentFolder = '/'
        NewFile = DummyFileUpload('blank.pdf')

        # first one goes up fine, as expected
        expected = {'param_string': '0'}
        self.login('admin')
        actual = self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()
        self.assertEqual(d2t(expected), d2t(actual))

        # now let's upload it again; the spec calls for auto-renaming the file
        expected = {'param_string': "201, 'blank(1).pdf'"}
        self.login('admin')
        actual = self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()
        self.assertEqual(d2t(expected), d2t(actual))


    def testMultipleNameCollision(self):
        Type = ''
        CurrentFolder = '/Docs'
        NewFile = DummyFileUpload('blank.pdf')

        # upload a whole mess of files
        self.login('admin')
        for i in range(25):
            self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()

        # and see what we find
        expected = [ 'blank.pdf', 'blank(1).pdf', 'blank(2).pdf'
                   , 'blank(3).pdf', 'blank(4).pdf', 'blank(5).pdf'
                   , 'blank(6).pdf', 'blank(7).pdf', 'blank(8).pdf'
                   , 'blank(9).pdf', 'blank(10).pdf', 'blank(11).pdf'
                   , 'blank(12).pdf', 'blank(13).pdf', 'blank(14).pdf'
                   , 'blank(15).pdf', 'blank(16).pdf', 'blank(17).pdf'
                   , 'blank(18).pdf', 'blank(19).pdf', 'blank(20).pdf'
                   , 'blank(21).pdf', 'blank(22).pdf', 'blank(23).pdf'
                   , 'blank(24).pdf'
                    ]
        actual = self.portal.Docs.objectIds()
        self.assertEqual(expected, actual)


    def testOutOfSequenceNames(self):
        Type = ''
        CurrentFolder = '/Docs'

        self.login('admin')

        # prime the pumps
        OriginalFile = DummyFileUpload('blank.pdf')
        self.fckc.FileUpload(Type, CurrentFolder, OriginalFile)

        # mess with the pumps
        RenamedFile = DummyFileUpload('blank(4).pdf')
        self.fckc.FileUpload(Type, CurrentFolder, RenamedFile)
        self.fckc.FileUpload(Type, CurrentFolder, OriginalFile)

        self.logout()

        expected = ['blank.pdf', 'blank(4).pdf', 'blank(5).pdf']
        actual = self.portal.Docs.objectIds()
        self.assertEqual(expected, actual)

    def testBigNumberedNames(self):
        Type = ''
        CurrentFolder = '/Docs'

        self.login('admin')

        # prime the pumps
        OriginalFile = DummyFileUpload('blank.pdf')
        self.fckc.FileUpload(Type, CurrentFolder, OriginalFile)

        # mess with the pumps
        RenamedFile = DummyFileUpload('blank(999923490303934890).pdf')
        self.fckc.FileUpload(Type, CurrentFolder, RenamedFile)
        self.fckc.FileUpload(Type, CurrentFolder, OriginalFile)

        self.logout()


        expected = [ 'blank.pdf'
                   , 'blank(999923490303934890).pdf'
                   , 'blank(999923490303934891).pdf'
                    ]
        actual = self.portal.Docs.objectIds()
        self.assertEqual(expected, actual)

    def testEmptyParensHandledProperly(self):
        Type = ''
        CurrentFolder = '/Docs'
        NewFile = DummyFileUpload('blank().pdf')

        self.login('admin')
        self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()

        expected = [ 'blank().pdf'
                   , 'blank()(1).pdf'
                    ]
        actual = self.portal.Docs.objectIds()
        self.assertEqual(expected, actual)

    def testNoExtensionHandledProperly(self):
        Type = ''
        CurrentFolder = '/Docs'
        NewFile = DummyFileUpload('blank')

        self.login('admin')
        self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()

        expected = [ 'blank'
                   , 'blank(1)'
                    ]
        actual = self.portal.Docs.objectIds()
        self.assertEqual(expected, actual)

    def testMultipleDotsHandledProperly(self):
        Type = ''
        CurrentFolder = '/Docs'
        NewFile = DummyFileUpload('blank.foo.hey.pdf')

        self.login('admin')
        self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.fckc.FileUpload(Type, CurrentFolder, NewFile)
        self.logout()

        expected = [ 'blank.foo.hey.pdf'
                   , 'blank.foo.hey(1).pdf'
                    ]
        actual = self.portal.Docs.objectIds()
        self.assertEqual(expected, actual)


##
# Assemble into a suite and run
##

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test))
    return suite

if __name__ == '__main__':
    framework()
