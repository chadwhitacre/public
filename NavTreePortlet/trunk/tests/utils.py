
from UserDict import UserDict

class Session(UserDict):
    def set(self, key, value):
        self.__setitem__(key, value)

def setupDummySession(request):
    request['SESSION'] = Session()

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)

