import os
import unittest

from httpy.Configuration import ConfigError
from httpy.Configuration import Configuration


class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.removeTestSite()
        self.buildTestSite()
        self.config = Configuration()

    def removeTestSite(self):
        if not os.path.isdir('root'):
            return
        for root, dirs, files in os.walk('root', topdown=False):
            for name in dirs:
                os.rmdir(os.path.join(root, name))
            for name in files:
                os.remove(os.path.join(root, name))
        os.rmdir('root')

    def dict2tuple(d):
        out = []
        for k, v in d.items():
            out.append((k, v))
        return sorted(out)
    dict2tuple = staticmethod(dict2tuple)

    def tearDown(self):
        self.removeTestSite()
