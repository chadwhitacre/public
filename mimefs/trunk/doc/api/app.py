"""Documentation widget for mimefslib. This is an httpy app.
"""
import inspect
import pydoc
import re
import string
import time

from httpy.Response import Response


# Define docstring formatters.
# ============================
# Set up to use reStructuredText if we have it.

def _pre(s):
    """This needs to be smarter
    """
    s = s.splitlines()
    for i in range(len(s)):
        if s[i].startswith('        '):
            s[i] = s[i][8:]
    return '<pre class="noshade">%s</pre>' % '\n'.join(s)

try:
    from docutils.core import publish_string
    BODY = re.compile('.*?<body>(.*?)</body>.*', re.DOTALL)
    def _reST(s):
        doc = publish_string(s, writer_name='html')
        return BODY.match(doc).group(1)
except:
    _reST = False


PARAMS = re.compile(' *def .*?\(self(?:, )?(.*?)\).*', re.DOTALL)


class Application:

    def respond(self, request):

        if request.method != 'GET':
            raise Response(501)
        if self.uri_root != '/' and request.path.startswith(self.uri_root):
            request.fullpath = request.path
            request.path = request.path[len(self.uri_root):]
        if request.path == '':
            raise Response(302, '', {'Location':self.uri_root+'/'})


        # Translate the URL path to an object path.
        # =========================================

        objpath = request.path
        want_routine = False
        if objpath.endswith('.html'):
            objpath = objpath[:-5]
            want_routine = True
        elif objpath.endswith('/'):
            objpath = objpath.rstrip('/')
        objnames = [n for n in objpath.split('/') if n]
        acceptable = string.ascii_letters + string.digits
        for name in objnames: # prevent snooping
            if name[0].isdigit():
                raise Response(404)
            for c in name:
                if c not in acceptable:
                    raise Response(404)
        objpath = '.'.join(objnames)


        # Generate a list of (objpath, object) tuples.
        # ============================================

        objs = []
        for i in range(len(objnames)):
            curpath = '.'.join(objnames[:i+1])
            obj = pydoc.locate(curpath)
            if obj is None:
                raise Response(404)
            objs.append((curpath, obj))
        obj = pydoc.locate(objpath)
        if want_routine and not inspect.isroutine(obj):
            raise Response(404)
        elif (not want_routine) and not request.path.endswith('/'):
            raise Response(302, '', {'Location':request.fullpath+'/'})


        data = {}

        data['title'] = objpath
        data['crumbs'] = self.getcrumbs(objs)
        data['nav'] = '' # self.getnav(obj)
        data['call'] = '' # self.getcall(obj)
        data['content'] = '' # self.getcontent(obj)

        data['version'] = ''
        if hasattr(obj, '__version__'):
            data['version'] = obj.__version__
        data['date'] = time.strftime('%B %d, %Y')
        data['base'] = self.uri_root

        response = Response(200)
        response.headers = {'Content-Type':'text/html'}
        response.body = TEMPLATE % data
        raise response


    def getcrumbs(self, objs):
        tmpl = '<a href="%s/%s%s">%s</a>'
        crumbs = []
        for path, obj in objs:
            ending = '/'
            if inspect.isroutine(obj):
                ending = '.html'
            crumbs.append(tmpl % ( self.uri_root
                                 , path.replace('.', '/')
                                 , ending
                                 , obj.__name__
                                  ))
        return '.'.join(crumbs)


    def getnav(self, obj):
        return ''
        """
        tmpl = '    <li><a href="%s">%s</a></li>'
        nav = [tmpl % ('/', 'top')]
        for c in callables:
            item = tmpl % ('%s/%s.html' % (self.uri_root, c), c)
            nav.append(item)
        nav = '\n'.join(nav)

        # Definition
        source = inspect.getsource(obj)
        params = PARAMS.match(source).group(1).replace('\n', '')
        data['title'] = '%s(%s)' % (name, params)
        """

        return nav

    def getcall(self, obj):
        """
        """
        return ''

    def getcontent(self, objpath):
        """Given an object, return a documentation body.
        """
        # find a module, look for a __docformat__



        format = _pre
        if hasattr(obj, '__docformat__'):
            if obj.__docformat__ == 'reStructuredText':
                if _reST:
                    format = _reST
        return format(obj.__doc__)




TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" lang="en-US">

<head profile="http://www.w3.org/2000/08/w3c-synd/#">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>%(title)s</title>
    <style>@import url("%(base)s/../style.css");</style>
</head>

<body>

<h1>%(crumbs)s</h1>

<div id="canvas">

    <div id="nav"><div id="nav-hack">
        %(nav)s
    </div></div>

    <div id="content"><div id="content-hack">

        %(call)s

        %(content)s

    </div></div>

    <br style="clear: both;" />

</div>

<hr />

<div id="footer">

    <p>This page was automatically generated from documentation in the source
    code on %(date)s. This documentation refers to version %(version)s.</p>

    <p><a href="http://www.zetadev.com/"> is Zeta software</a>.</p>

</div>

</body>
"""