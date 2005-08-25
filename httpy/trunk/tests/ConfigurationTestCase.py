import os
import unittest

from httpy.Configuration import ConfigError
from httpy.Configuration import Configuration


class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.scrubenv()
        self.config = Configuration()

    def dict2tuple(d):
        out = []
        for k, v in d.items():
            out.append((k, v))
        return sorted(out)
    dict2tuple = staticmethod(dict2tuple)

    def scrubenv(self):
        save = {}
        for opt in Configuration.options:
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
