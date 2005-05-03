import os, sys, time
from pprint import pprint
import unittest

# make sure we can find ourselves
sys.path.insert(1, os.path.realpath('..'))

# the thing we want to test
from FCKeditor import FCKeditor, FCKexception
from FCKconnector import FCKconnector


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
        self.fck.SetConfig('AutoDetectLanguage','false')
        self.fck.SetConfig('DefaultLanguage','pt-BR')
        qs = self.fck.GetConfigQuerystring()
        self.failUnlessEqual(qs, "AutoDetectLanguage=false&DefaultLanguage=pt-BR")

    def testUrlEncodedConfig(self):
        self.fck.SetConfig('foo','&I need:  "URL encoding"')
        self.fck.SetConfig('so do *I*','bar')
        qs = self.fck.GetConfigQuerystring()
        self.failUnlessEqual(qs,"foo=%26I+need%3A++%22URL+encoding%22" +\
                                 "&so+do+%2AI%2A=bar")

    def testDefaultReplacement(self):
        expected = """\
<div>
    <input type="hidden"
           id="MyEditor"
           name="MyEditor"
           value="" />
    <input type="hidden"
           id="MyEditor___Config"
           value="" />
    <iframe id="MyEditor___Frame"
            src="/FCKeditor/editor/fckeditor.html?InstanceName=MyEditor&Toolbar=Default"
            width="100%" height="200px"
            frameborder="no" scrolling="no"></iframe>
</div>"""

        self.fck.SetCompatible('Gecko/20030313')
        self.assertEqual(self.fck.Create(), expected)


    def testCustomReplacement(self):
        self.fck.SetConfig('AutoDetectLanguage','false')
        self.fck.SetConfig('DefaultLanguage','pt-BR')
        self.fck.InstanceName = 'CustomEditor'
        self.fck.Width = 300  # int should be converted to '300px'
        self.fck.Height = 400
        self.fck.ToolbarSet = 'CustomToolbar'
        self.fck.BasePath = '/AltPath/'
        self.fck.Value = """\
<html>
<head>
    <title>TEST</title>
</head>
<body>
    Foo.
</body>
</html>
        """

        expected = """\
<div>
    <input type="hidden"
           id="CustomEditor"
           name="CustomEditor"
           value="%3Chtml%3E%0A%3Chead%3E%0A++++%3Ctitle%3ETEST%3C%2Ftitle%3E%0A%3C%2Fhead%3E%0A%3Cbody%3E%0A++++Foo.%0A%3C%2Fbody%3E%0A%3C%2Fhtml%3E%0A++++++++" />
    <input type="hidden"
           id="CustomEditor___Config"
           value="AutoDetectLanguage=false&DefaultLanguage=pt-BR" />
    <iframe id="CustomEditor___Frame"
            src="/AltPath/editor/fckeditor.html?InstanceName=CustomEditor&Toolbar=CustomToolbar"
            width="300px" height="400px"
            frameborder="no" scrolling="no"></iframe>
</div>"""

        self.fck.SetCompatible('Gecko/20030313')
        self.assertEqual(self.fck.Create(), expected)



    def testCompatible(self):
        compatible_useragents = """\
Mozilla/5.0 (X11; U; Linux i586; en-US; rv:1.3) Gecko/20030313
Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.5a) Gecko/20030718
Mozilla/5.0 (Windows; U; Windows NT 5.1; de-DE; rv:1.5a) Gecko/20030728 Mozilla Firebird/0.6.1
Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.5) Gecko/20031016 K-Meleon/0.8.1
Mozilla/5.0 (X11; U; Linux i686; en-US) Gecko/20031007 Firebird/0.7
Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.6) Gecko/20040210 Firefox/0.8
Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.2) Gecko/20040803 MultiZilla/1.6.4.0b
Mozilla /4.0 (compatible; MSIE 6.0; i686 Linux)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; YPC 3.0.3; sbcydsl 3.12; FunWebProducts; Alexa Toolbar)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; Rogers Hi-Speed Internet; iebar; .NET CLR 1.1.4322)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; Maxthon; FREE; .NET CLR 1.1.4322; .NET CLR 2.0.40607)
Mozilla/4.0 (compatible; MSIE 6.0b; Windows 98; GTelnet1.0)
Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.23 [es-ES]
Mozilla/5.0 Opera/7.0 (X11; U; Linux i686; de-DE; rv:1.6) Gecko/20040114
Mozilla/4.0 (compatible; MSIE 5.5; AOL 8.0; Windows 98; Win 9x 4.90; .NET CLR 1.1.4322)
Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 4.0; Version 2/5.5 Customised)
Mozilla/4.0 (compatible; MSIE 5.5; Windows NT 5.0);JTB:104:a95eef30-9f35-4ec0-bc43-66a16a703faf
        """

        i = 0
        for useragent in compatible_useragents.split(os.linesep):
            i += 1
            if useragent.strip():
                self.failUnless(self.fck.SetCompatible(useragent),
                                "compatible failed on #%s: %s" % (i, useragent))


    def testIncompatible(self):
        incompatible_useragents = """\
Mozilla/5.0 (X11; U; Linux i686; en-US; rv:0.9.9) Gecko/20020513
Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.2.1) Gecko/20021130
Mozilla/4.0 (AmigaOS 3.1)
Mozilla/4.0 (compatible; MSIE 5.01; Windows NT 5.0; DigExt; iebar; (R1 1.5))
Mozilla/4.0 (compatible; MSIE 5.0; Mac_PowerPC; S425166QXM03307)
Mozilla/4.0 (compatible; MSIE 5.01; Windows 95; QXW0332b)
Mozilla/4.0 (compatible; MSIE 5.0; Windows 95) Opera 5.12 [en]
Opera/7.11 (Linux 2.4.18-xfs i686; U) [en]
Opera/7.50 (Windows NT 5.2; U) [en]
Opera/8.00 (Windows; U)
Opera/7.54 (FreeBSD; U)
        """

        i = 0
        for useragent in incompatible_useragents.split(os.linesep):
            i += 1
            if useragent.strip():
                self.failIf(self.fck.SetCompatible(useragent),
                            "incompatible failed on #%s: %s" % (i, useragent))


class TestFCKeditor(unittest.TestCase):

    def setUp(self):
        self.fck = FCKconnector()

    def testGoodData(self):
        data = { 'CommandName'  : 'GetFolders'
               , 'ResourceType' : 'Image'
               , 'FolderPath'   : '/path/to/content/'
               , 'ServerPath'   : '/'
                }
        self.assertEqual(self.fck._validate(data), data)

    def testAllCommands(self):
        data = { 'ResourceType' : 'Image'
               , 'FolderPath'   : '/path/to/content/'
               , 'ServerPath'   : '/'
                }

        data['CommandName'] = 'GetFolders'
        self.assertEqual(self.fck._validate(data), data)

        data['CommandName'] = 'GetFoldersAndFiles'
        self.assertEqual(self.fck._validate(data), data)

        data['CommandName'] = 'CreateFolder'
        self.assertEqual(self.fck._validate(data), data)

        data['CommandName'] = 'FileUpload'
        self.assertEqual(self.fck._validate(data), data)

    def testBadCommand(self):
        data = { 'CommandName'  : 'YADAYADAYADA'
               , 'ResourceType' : 'Image'
               , 'FolderPath'   : '/path/to/content/'
               , 'ServerPath'   : '/'
                }
        self.assertRaises(FCKexception, self.fck._validate, data)

    def testAllResourceTypes(self):
        data = { 'CommandName'  : 'GetFolders'
               , 'FolderPath'   : '/path/to/content/'
               , 'ServerPath'   : '/'
                }

        data['ResourceType'] = 'File'
        self.assertEqual(self.fck._validate(data), data)

        data['ResourceType'] = 'Image'
        self.assertEqual(self.fck._validate(data), data)

        data['ResourceType'] = 'Flash'
        self.assertEqual(self.fck._validate(data), data)

        data['ResourceType'] = 'Media'
        self.assertEqual(self.fck._validate(data), data)

    def testBadResourceType(self):
        data = { 'CommandName'  : 'GetFolders'
               , 'ResourceType' : 'Audio'
               , 'FolderPath'   : '/path/to/content/'
               , 'ServerPath'   : '/'
                }
        self.assertRaises(FCKexception, self.fck._validate, data)

    def testFolderPath(self):
        data = { 'CommandName'  : 'GetFolders'
               , 'ResourceType' : 'Image'
               , 'ServerPath'   : '/'
                }

        # must start and end with a forward slash
        data['FolderPath'] = '/Docs/Test/'
        self.assertEqual(self.fck._validate(data), data)

        data['FolderPath'] = '/'
        self.assertEqual(self.fck._validate(data), data)

        # bad data
        data['FolderPath'] = 'Docs/Test/'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['FolderPath'] = '/Docs/Test'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['FolderPath'] = ''
        self.assertRaises(FCKexception, self.fck._validate, data)

    def testServerPath(self):
        data = { 'CommandName'  : 'GetFolders'
               , 'ResourceType' : 'Image'
               , 'FolderPath'   : '/'
                }

        # must start and end with a forward slash
        data['ServerPath'] = '/Docs/Test/'
        self.assertEqual(self.fck._validate(data), data)

        data['ServerPath'] = '/'
        self.assertEqual(self.fck._validate(data), data)


        # bad data
        data['ServerPath'] = 'Docs/Test/'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['ServerPath'] = '/Docs/Test'
        self.assertRaises(FCKexception, self.fck._validate, data)

        data['ServerPath'] = ''
        self.assertRaises(FCKexception, self.fck._validate, data)




if __name__ == '__main__':
    unittest.main()
