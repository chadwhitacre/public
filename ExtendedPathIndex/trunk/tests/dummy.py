class Dummy:

    meta_type="foo"

    def __init__( self, path):
        self.path = path

    def getPhysicalPath(self):
        return self.path.split('/')

    def __str__( self ):
        return '<Dummy: %s>' % self.path

    __repr__ = __str__

