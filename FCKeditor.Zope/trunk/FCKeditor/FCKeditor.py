"""

should Config settings be changed at run time? or should we have multiple
instances of FCKeditor, all with separate settings? since the thing you really
want to change from instance to instance is the composition of the toolbar, and
toolbars themselves are not defined here, but rather in the fckConfig.js file,
then I think it makes sense for this to be a single object


"""
import re
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


class FCKexception(Exception):
    pass


class FCKeditor:
    """ provides API for tuning and instantiating an FCKeditor DHTML widget
    """

    def __init__(self, *args, **kw):

        # defaults -- using instance attrs instead of class attrs so we can
        # use self.__dict__
        self.InstanceName        = 'MyEditor'
        self.Width               = '100%'
        self.Height              = '200px'
        self.ToolbarSet          = 'Default'
        self.Value               = ''
        self.BasePath            = '/FCKeditor/'
        self.ConfigQuerystring   = ''

        # clean up InstanceName
        if kw.has_key('InstanceName'):
            kw['InstanceName'] = self._scrub(kw['InstanceName'])

        # custom
        self.__dict__.update(kw)

        self.Config         = {}

    _bad_InstanceName = re.compile(r'[^a-zA-Z0-9-]')
    def _scrub(self, InstanceName):
        """given an id, make it safe for use as an InstanceName, which is used
        as a CSS identifier
        """
        InstanceName = self._bad_InstanceName.sub('-', InstanceName)
        while not InstanceName[:1].isalpha(): # can only start with a letter
            InstanceName = InstanceName[1:]
        return InstanceName

    def Create(self):
        """return an HTML snippet which instantiates an FCKeditor or a plain
        textarea
        """

        if not hasattr(self, 'Compatible'):
            raise FCKexception, "You must run the setCompatible method first"

        # quote the initial HTML value
        self.Value = quote_plus(self.Value)

        # marshall config into a querystring (only used for compatible)
        self.ConfigQuerystring = self.GetConfigQuerystring()

        # parse width & height
        if str(self.Width).isdigit():  self.Width  = '%spx' % self.Width
        if str(self.Height).isdigit(): self.Height = '%spx' % self.Height

        if self.Compatible:
            return FCKtemplates.COMPATIBLE % self.__dict__
        else:
            return FCKtemplates.INCOMPATIBLE % self.__dict__

    def SetCompatible(self, useragent):
        """given a browser's user-agent string, set a boolean on self
        """

        useragent = useragent.lower()
        Compatible = False # default

    	# Internet Explorer
        """Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)"""
    	match = re.search(r'msie (\d*\.\d*)', useragent)
    	if match is not None:
    	    version = match.group(1)
    	    if version is not None:
        	    Compatible = float(version) >= 5.5

    	# Gecko
        """Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.7.7) Gecko/20050414 Firefox/1.0.3"""
    	match = re.search(r'gecko/(\d*)', useragent)
    	if match is not None:
    	    version = match.group(1)
    	    if version is not None:
	            Compatible = int(version) >= 20030210

        self.Compatible = Compatible
        return Compatible

    def GetConfigQuerystring(self):
        """marshall our Config settings into a querystring
        """
        c = self.Config
        q = quote_plus
        return '&'.join(['%s=%s' % (q(key), q(c[key])) for key in c])

    def SetConfig(self, key, value):
        self.Config[key] = value
