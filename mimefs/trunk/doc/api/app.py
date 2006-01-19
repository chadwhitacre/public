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
    return '<pre class="noshade">%s</pre>' % s

try:
    from docutils.core import publish_string
    BODY = re.compile('.*?<body>(.*?)</body>.*', re.DOTALL)
    def _reST(s):
        if not isinstance(s, basestring):
            return ''
        doc = publish_string(s, writer_name='html')
        return BODY.match(doc).group(1)
except:
    _reST = False


PARAMS = re.compile(' *def .*?\(self(?:, )?(.*?)\).*', re.DOTALL)


class Application:

    def respond(self, request):

        # Preen the request.
        # ==================

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
        acceptable = string.ascii_letters + string.digits + '_'
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
            obj = pydoc.locate(curpath, forceload=True)
            if obj is None:
                raise Response(404)
            objs.append((curpath, obj))
        if want_routine and not inspect.isroutine(obj):
            raise Response(404)
        elif (not want_routine) and not request.path.endswith('/'):
            raise Response(302, '', {'Location':request.fullpath+'/'})


        # Build a data structure.
        # =======================
        # This will be passed as a string replacement dictionary to TEMPLATE.
        # By the time we get here, we have objpath, obj, objnames and objs.

        data = {}

        data['title'] = objpath
        data['crumbs'] = self.getcrumbs(objs, obj)
        data['nav'] = self.getnav(objpath, objs)
        data['callable'] = self.getcallable(obj, objnames[-1])
        data['content'] = self.getcontent(objs, obj)

        data['version'] = ''
        if hasattr(obj, '__version__'):
            data['version'] = obj.__version__
        data['date'] = time.strftime('%B %d, %Y')
        data['base'] = self.uri_root


        # Send it out.
        # ============

        response = Response(200)
        response.headers = {'Content-Type':'text/html'}
        response.body = TEMPLATE % data
        raise response



    def getcrumbs(self, objs, curobj):
        """Return a list of links to all parent packages, modules, and classes.
        """
        have_class = inspect.isclass(curobj)
        tmpl = '<a href="%s/%s%s">%s</a>'
        crumbs = []
        for path, obj in objs:
            if inspect.isroutine(obj):
                break
            if have_class and inspect.isclass(obj):
                break
            ending = '/'
            if inspect.isroutine(obj):
                ending = '.html'
            crumbs.append(tmpl % ( self.uri_root
                                 , path.replace('.', '/')
                                 , ending
                                 , obj.__name__.split('.')[-1]
                                  ))
        return '.'.join(crumbs)


    def getcallable(self, obj, objname):
        """Return an HTML snippet about the closest callable object.
        """

        paratmpl = ' <span class="params">%s</span>'
        objtype = ''

        if inspect.isclass(obj):
            objtype = 'class'
            if '__init__' in obj.__dict__:
                # hasattr finds builtin.__init__, which confuses
                # inspect.isfunction (called via getargspec)
                func = getattr(obj, '__init__')
            else:
                func = False
                params = paratmpl % '()'
        elif inspect.isroutine(obj):
            if inspect.ismethod(obj):
                objtype = 'method'
            else:
                objtype = 'function'
            func = obj
        else:
            return ''

        if func:
            args = inspect.getargspec(func)
            params = inspect.formatargspec(*args)
            params = params.replace('self, ', '').replace('self', '')
            params = paratmpl % params

        return '<h1>%s%s<span class="type">%s</span></h1>' % ( objname
                                                             , params
                                                             , objtype
                                                              )


    def getnav(self, objpath, objs):
        """Return an HTML list of members for the closest module/package/class.
        """

        # Find the object to generate navigation from.
        # ============================================

        curobj = objs[-1][1]
        navleader = curobj
        if inspect.isroutine(curobj):
            navleader = objs[-2][1]
            objpath = '.'.join(objpath.split('.')[:-1])


        # Get all public members.
        # =======================
        # An explicit __all__ is always obeyed, but we only do magic for
        # classes. This is because module namespaces usually have tons of junk
        # and only a little good stuff, whereas the opposite is usually true
        # for class namespaces. Public members are sorted into packages/modules,
        # methods/functions, and other.

        magic = False
        if hasattr(navleader, '__all__'):
            all = navleader.__all__
        else:
            if inspect.isclass(navleader):
                all = [n for n in navleader.__dict__ if not n.startswith('_')]
                magic = True
            else:
                # Nothing to navigate.
                return ''

        members = [(n, getattr(navleader, n)) for n in all]

        packages = []
        modules = []
        classes = []
        routines = []
        values = []

        for m in members:
            if inspect.isroutine(m[1]):
                routines.append(m)
            elif inspect.isclass(m[1]):
                classes.append(m)
            elif magic:
                values.append(m)
            elif self.ispackage(m[1]):
                packages.append(m)
            else:
                modules.append(m)


        # Build the HTML.
        # ===============

        html = []

        curtmpl = '    <li class="current">%s</a></li>'
        linktmpl = '    <li><a href="%s">%s</a></li>'
        constmpl = '    <dt>%s</dt>\n<dd>%s</dd>'


        if packages:
            html.append('<h3>Packages</h3>')
            html.append('<ul>')
            for name, obj in packages:
                if obj.__name__ == curobj.__name__:
                    item = curtmpl % name
                else:
                    url = '%s/%s/%s/' % ( self.uri_root
                                         , objpath.replace('.', '/')
                                         , name
                                          )
                    item = linktmpl % (url, name)
                html.append(item)
            html.append('</ul>')


        if modules:
            html.append('<h3>Modules</h3>')
            html.append('<ul>')
            for name, obj in modules:
                if obj.__name__ == curobj.__name__:
                    item = curtmpl % name
                else:
                    url = '%s/%s/%s/' % ( self.uri_root
                                         , objpath.replace('.', '/')
                                         , name
                                          )
                    item = linktmpl % (url, name)
                html.append(item)
            html.append('</ul>')


        if classes:
            html.append('<h3>Classes</h3>')
            html.append('<ul>')
            for name, obj in classes:
                if obj.__name__ == curobj.__name__:
                    item = curtmpl % name
                else:
                    url = '%s/%s/%s/' % ( self.uri_root
                                         , objpath.replace('.', '/')
                                         , name
                                          )
                    item = linktmpl % (url, name)
                html.append(item)
            html.append('</ul>')


        if routines:
            heading = inspect.isclass(navleader) and 'Methods' or 'Functions'
            html.append('<h3>%s</h3>' % heading)
            html.append('<ul>')
            for name, obj in routines:
                if obj.__name__ == curobj.__name__:
                    item = curtmpl % name
                else:
                    url = '%s/%s/%s.html' % ( self.uri_root
                                         , objpath.replace('.', '/')
                                         , name
                                          )
                    item = linktmpl % (url, name)
                html.append(item)
            html.append('</ul>')


        if values:
            html.append('<h3>Values</h3>')
            html.append('<dl>')
            for name, val in values:
                html.append(constmpl % (name, val))
            html.append('</dl>')


        return '\n'.join(html)


    def ispackage(self, obj):
        if not hasattr(obj, '__file__'):
            return False
        return '__init__' in obj.__file__


    def getcontent(self, objs, curobj):

        if not curobj.__doc__:
            return ''


        # Trim initial spaces from docstring lines.
        # =========================================

        lines = curobj.__doc__.splitlines()
        numspaces = 0
        for i in range(len(lines)):
            line = lines[i]
            if (not numspaces) and i>0 and line:
                numspaces = len(line) - len(line.lstrip())
            if line.startswith(' '*numspaces):
                lines[i] = line[numspaces:]
        doc = '\n'.join(lines)


        # Find a formatter to use.
        # ========================

        format = _pre
        for name, obj in reversed(objs):
            if inspect.ismodule(obj):
                if hasattr(obj, '__docformat__'):
                    rest = ('rest', 'restructuredtext')
                    if obj.__docformat__.lower() in rest:
                        if _reST:
                            format = _reST

        # Use it.
        # =======

        return format(doc)




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

<h2>%(crumbs)s</h2>

%(callable)s

<div id="canvas">

    <div id="nav"><div id="nav-hack">
        %(nav)s
    </div></div>

    <div id="content"><div id="content-hack">
        %(content)s
    </div></div>

    <div style="clear: both; height: 0px;">&nbsp;</div>

</div>

<hr />

<div id="footer">

    <p>This document was automatically generated from this object's source code
    on %(date)s.</p>

    <p><a href="http://www.zetadev.com/"> is Zeta software</a>.</p>

</div>

</body>
"""