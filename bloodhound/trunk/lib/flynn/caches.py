import os
import stat

from httpy.utils import log

from acn.navigator import Navigator
from acn.lehuen import Cache, NOT_INITIALIZED
from zope.pagetemplate.pagetemplatefile import PageTemplateFile


class NavCache(Cache):
    """Cache for nav structures.
    """

    def __init__(self):
        """Extend to hardwire size and adapt to mode.

        The max_size is just a safety belt. If you have that many nav arcs in
        your static site, then you need to consider moving to a database-driven
        architecture. :^)

        In modes other than deployment, we are just a passthrough.

        """
        Cache.__init__(self, max_size=1000)
        deploy_mode = os.environ.get('HTTPY_MODE', 'deployment') == 'deployment'
        self.deploy_mode = deploy_mode


    def __call__(self):
        """Singleton.
        """
        return self


    def check(self, key, name, entry):
        """Checks to see if a given nav structure is out of date.

        Since these pages aren't really designed to be changed once the site is
        running, I think we should just populate the cache as needed and never
        expire it. In other words, any change to the nav structure will require
        a reboot (in deployment mode, of course).

        """

        if not self.deploy_mode:
            return key
        elif entry._value is NOT_INITIALIZED:
            return key
        else:
            return None


    def build(self, key, name, opened, entry):
        """The key is a filesystem path; returns a template object.
        """
        log(86, "Loading nav for %s" % str(key))
        navgen = Navigator()
        navgen.top = key[0]
        navgen.bottom = key[1]
        return navgen()

NavCache = NavCache()



class TemplateCache(Cache):
    """Cache for Zope Page Templates.
    """

    def __init__(self):
        """Extend to hardwire size and adapt to mode.

        The max_size is just a safety belt. If you have that many pages in your
        static site, then you need to consider moving to a database-driven
        architecture. :^)

        In modes other than deployment, we are just a passthrough.

        """
        Cache.__init__(self, max_size=1000)
        deploy_mode = os.environ.get('HTTPY_MODE', 'deployment') == 'deployment'
        self.deploy_mode = deploy_mode


    def __call__(self):
        """Singleton.
        """
        return self


    def check(self, key, name, entry):
        """Compares the mod time of the file with the timestamp of our version.
        """

        if not self.deploy_mode:
            # No caching in dev/deb mode
            return key

        timestamp = os.stat(key)[stat.ST_MTIME]
        if entry._value is NOT_INITIALIZED:
            entry._timestamp = timestamp
            return key
        elif entry._timestamp != timestamp:
            entry._timestamp = timestamp
            return key
        else:
            return None


    def build(self, key, name, opened, entry):
        """The key is a filesystem path; returns a template object.
        """
        log(86, "Loading template from %s" % key)
        prefix, path = os.path.split(key)
        return PageTemplateFile(path, prefix)

TemplateCache = TemplateCache()
