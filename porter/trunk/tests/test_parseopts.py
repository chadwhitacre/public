import unittest
from porter import PorterCmd

class TestPorter(unittest.TestCase):

    def test_parseopts(self):
        line = "ls -l"
        opts = PorterCmd.parseopts(line)
        self.assertEqual(opts, ['l'])

if __name__ == '__main__':
    unittest.main()