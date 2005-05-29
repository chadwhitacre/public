def dict2tuple(d):
    """convert a dictionary to a sorted list of tuples
    """
    l = [(k, d[k]) for k in d]
    l.sort()
    return l

class DummyFileUpload(file):
    filename = ''
    headers = {'content-type':'application/octet-stream'} # whatever
    def __init__(self, filename):
        self.filename = filename
        file.__init__(self, 'blank.pdf')
    def __repr__(self):
        return "<DummyFileUpload named '%s'>" % self.filename
