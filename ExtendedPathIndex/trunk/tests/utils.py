
from UserDict import UserDict

class Session(UserDict):
    def set(self, key, value):
        self.__setitem__(key, value)

def setupDummySession(request):
    request['SESSION'] = Session()

def setupGlobalRequest(request):
    from ZPublisher import Publish
    from thread import get_ident
    Publish._requests[get_ident()] = request

def addLanguage(site, language):
    site.portal_languages.addSupportedLanguage(language)

def setLanguage(language):
    from Globals import get_request
    request = get_request()
    if request:
        request.cookies['I18N_CONTENT_LANGUAGE'] = language
        request.cookies['I18N_LANGUAGE'] = language
        request['set_language'] = language
        session = request.get('SESSION')
        session['pts_language'] = 'language'
        request.SESSION = session

def makeContent(context, portal_type, id='document', **kw ):
    context.invokeFactory( type_name=portal_type, id=id, **kw )
    content = getattr( context, id )
    return content

def makeTranslation(content, language='en', **kw ):
    content.addTranslation( language=language )
    return content.getTranslation(language)

def sortTuple(t):
    l = list(t)
    l.sort()
    return tuple(l)

