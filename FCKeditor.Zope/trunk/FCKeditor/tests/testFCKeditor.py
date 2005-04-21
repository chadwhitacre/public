import os, sys, time
from pprint import pprint
import unittest

# make sure we can find ourselves
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))


# the thing we want to test
from Products.FCKeditor.FCKeditor import FCKeditor


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
        #self.fck.config = {} # hmmm ... not sure why I need this
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

        self.assertEqual(self.fck.Create(), expected)



if __name__ == '__main__':
    unittest.main()

