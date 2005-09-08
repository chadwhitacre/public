import os
import unittest

from httpy.Config import ConfigError
from httpy.Config import Config


class ConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.scrubenv()
        self.config = Config()
        for app in ('app1', 'app2'):
            if os.path.isdir(app):
                os.rmdir(app)
            os.mkdir(app)

    def dict2tuple(d):
        return tuple(sorted(d.iteritems()))
    dict2tuple = staticmethod(dict2tuple)

    def scrubenv(self):
        save = {}
        for opt in Config.options:
            envvar = 'HTTPY_%s' % opt.upper()
            if os.environ.has_key(envvar):
                save[envvar] = os.environ[envvar]
                del os.environ[envvar]
        self.env = save

    def restoreenv(self):
        for k, v in self.env.items():
            os.environ[k] = v
        self.env = {}

    def tearDown(self):
        self.restoreenv()
        if os.path.isfile('httpy.conf'):
            os.remove('httpy.conf')
        for app in ('app1', 'app2'):
            if os.path.isdir(app):
                os.rmdir(app)
