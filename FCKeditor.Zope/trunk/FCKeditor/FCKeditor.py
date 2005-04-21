"""

should config settings be changed at run time? or should we have multiple
instances of FCKeditor, all with separate settings? since the thing you really
want to change from instance to instance is the composition of the toolbar, and
toolbars themselves are not defined here, but rather in the fckconfig.js file,
then I think it makes sense for this to be a single object


"""
import urllib


COMPATIBLE_TEMPLATE = """\
<div>
    <input type="hidden"
           id="%(instance_name)s"
           name="%(instance_name)s"
           value="%(value)s" />
    <input type="hidden"
           id="%(instance_name)s___Config"
           value="%(config_querystring)s" />
    <iframe id="%(instance_name)sr___Frame"
            src="%(base_path)seditor/fckeditor.html?InstanceName=%(instance_name)s&Toolbar=%(toolbar_set)s"
            width="%(height)s" height="%(width)s"
            frameborder="no" scrolling="no"></iframe>
</div>"""

INCOMPATIBLE_TEMPLATE = """\
<div>
    <textarea name="%(instance_name)s"
              rows="4" cols="40"
              style="width: %(width)s; height: %(height)s;"
              wrap="virtual" />
        %(value)s
    </textarea>
</div>"""


class FCKeditor:
    """ provides API for server-side tuning and instantiation of an FCKeditor
    """

    def __init__(self, instance_name    = '/FCKeditor/'
                     , width            = '100%'
                     , height           = '200px'
                     , toolbar_set      = 'Default'
                     , value            = ''
                     , base_path        = '/'
                     , config           = {}
                      ):
        self.instance_name  = instance_name
        self.width          = width
        self.height         = height
        self.toolbar_set    = toolbar_set
        self.value          = value
        self.base_path      = base_path
        self.config         = config

    def __call__(self):
        return self.create()

    def create(self):
        """return an HTML snippet which instantiates the editor with our
        configuration
        """
        if compatible():
            self.config_querystring = self.get_config_querystring()
            return COMPATIBLE_TEMPLATE % self.__dict__
        else:
            return INCOMPATIBLE_TEMPLATE % self.__dict__

    def compatible(self):
        """only actually meaningful in Zope-space
        """
        return True

    def get_config_querystring(self):
        """marshall our config settings into a querystring
        """
        c = self.config
        q = urllib.quote_plus
        return '&'.join(['%s=%s' % (q(key), q(c[key])) for key in c])

    def set_config(self, key, value):
        self.config[key] = value
