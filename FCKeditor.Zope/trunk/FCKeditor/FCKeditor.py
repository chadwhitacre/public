"""

should Config settings be changed at run time? or should we have multiple
instances of FCKeditor, all with separate settings? since the thing you really
want to change from instance to instance is the composition of the toolbar, and
toolbars themselves are not defined here, but rather in the fckConfig.js file,
then I think it makes sense for this to be a single object


"""
from urllib import quote_plus

class FCKtemplates:

    COMPATIBLE = """\
<div>
    <input type="hidden"
           id="%(InstanceName)s"
           name="%(InstanceName)s"
           value="%(Value)s" />
    <input type="hidden"
           id="%(InstanceName)s___Config"
           value="%(ConfigQuerystring)s" />
    <iframe id="%(InstanceName)s___Frame"
            src="%(BasePath)seditor/fckeditor.html?InstanceName=%(InstanceName)s&Toolbar=%(ToolbarSet)s"
            width="%(Width)s" height="%(Height)s"
            frameborder="no" scrolling="no"></iframe>
</div>"""

    INCOMPATIBLE = """\
<div>
    <textarea name="%(InstanceName)s"
              rows="4" cols="40"
              style="Width: %(Width)s; Height: %(Height)s;"
              wrap="virtual" />
        %(Value)s
    </textarea>
</div>"""


class FCKeditor:
    """ provides API for server-side tuning and instantiation of an FCKeditor
    """

    def __init__(self, InstanceName     = 'MyEditor'
                     , Width            = '100%'
                     , Height           = '200px'
                     , ToolbarSet       = 'Default'
                     , Value            = ''
                     , BasePath         = '/FCKeditor/'
                      ):
        self.InstanceName   = InstanceName
        self.Width          = Width
        self.Height         = Height
        self.ToolbarSet     = ToolbarSet
        self.Value          = Value
        self.BasePath       = BasePath

        self.Config         = {}
        self.ConfigQuerystring = ''

    def __call__(self):
        return self.create()

    def Create(self):
        """return an HTML snippet which instantiates the editor with our
        configuration
        """

        # quote the initial HTML value
        self.Value = quote_plus(self.Value)

        # marshall config into a querystring (only used for compatible)
        self.ConfigQuerystring = self.GetConfigQuerystring()

        # parse width & height
        if str(self.Width).isdigit():  self.Width  = '%spx' % self.Width
        if str(self.Height).isdigit(): self.Height = '%spx' % self.Height

        # spit out either FCKeditor or a textarea
        if self.Compatible():
            return FCKtemplates.COMPATIBLE % self.__dict__
        else:
            return FCKtemplates.INCOMPATIBLE % self.__dict__

    def Compatible(self):
        """only actually meaningful in Zope-space
        """
        return True

    def GetConfigQuerystring(self):
        """marshall our Config settings into a querystring
        """
        c = self.Config
        q = quote_plus
        return '&'.join(['%s=%s' % (q(key), q(c[key])) for key in c])

    def SetConfig(self, key, value):
        self.Config[key] = value
