class TestCaseCitlib(unittest.TestCase):

    def setUp(self):
        self.cit = CitConn(listen=True)
        self.cit.USER('test')
        self.cit.PASS('testing')

    def tearDown(self):
        self.cit.LOUT()
        self.cit._sock.close()
