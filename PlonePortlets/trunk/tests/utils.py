
from UserDict import UserDict

class Session(UserDict):
    def set(self, key, value):
        self.__setitem__(key, value)

def setupDummySession(request):
    request['SESSION'] = Session()

def makeContent(context, portal_type, id='document', **kw ):
    context.invokeFactory( type_name=portal_type, id=id, **kw )
    content = getattr( context, id )
    return content

def makePortlet(context, portal_type='StaticPortlet', id='portlet', **kw ):
    context.invokeFactory( type_name=portal_type, id=id, **kw )
    content = getattr( context, id )
    return content

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)

