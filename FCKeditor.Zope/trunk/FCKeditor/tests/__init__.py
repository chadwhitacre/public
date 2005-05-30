def dict2tuple(d):
    """convert a dictionary to a sorted list of tuples
    """
    l = [(k, d[k]) for k in d]
    l.sort()
    return l

class DummyFileUpload(file):
    """Simulates a Zope FileUpload obj. Original is at:

      Products.ZPublisher.HTTPRequest.FileUpload

    """

    filename = ''
    headers = {'content-type':'application/octet-stream'} # whatever

    def __init__(self, filename):
        self.filename = filename
        if filename.endswith('jpg'):
            file.__init__(self, 'blank.jpg')
        else:
            file.__init__(self, 'blank.pdf')

    def __repr__(self):
        return "<DummyFileUpload named '%s'>" % self.filename
