"""Documentation widget for mimefslib. This is an httpy app.
"""
import inspect
import re
import time

from httpy.Response import Response

import mimefslib


PARAMS = re.compile(' *def .*?\(self(?:, )?(.*?)\).*', re.DOTALL)


class Application:

    def respond(self, request):

        if request.method != 'GET':
            raise Response(501)
        if self.uri_root != '/' and request.path.startswith(self.uri_root):
            request.path = request.path[len(self.uri_root):]
        if request.path == '':
            raise Response(302, '', {'Location':self.uri_root+'/'})


        # Gather callables.
        # =================

        callables = []
        for attr in mimefslib.Server.__dict__:
            if not attr.startswith('_'):
                callables.append(attr)
        callables.sort()


        # Build a dictionary.
        # ===================

        data = {}
        data['version'] = mimefslib.__version__
        data['date'] = time.strftime('%B %d, %Y')

        tmpl = '    <li><a href="%s">%s</a></li>'
        nav = [tmpl % ('/', 'top')]
        for c in callables:
            item = tmpl % ('%s/%s.html' % (self.uri_root, c), c)
            nav.append(item)
        data['nav'] = '\n'.join(nav)

        if request.path == '/':
            data['title'] = ''
            data['body'] = mimefslib.__doc__ % len(callables)
        elif request.path[1:-5] in callables:
            name = request.path[1:-5]
            m = getattr(mimefslib.Server, name)

            # Definition
            source = inspect.getsource(m)
            params = PARAMS.match(source).group(1).replace('\n', '')
            data['title'] = '%s(%s)' % (name, params)

            # Documentation
            doc = m.__doc__.splitlines()
            for i in range(len(doc)):
                if doc[i].startswith('        '):
                    doc[i] = doc[i][8:]
            data['body'] = '\n'.join(doc)

        else:
            raise Response(404)

        response = Response(200)
        response.headers = {'Content-Type':'text/html'}
        response.body = TEMPLATE % data
        raise response


TEMPLATE = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
                      "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en-US" lang="en-US">

<head profile="http://www.w3.org/2000/08/w3c-synd/#">
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>mimefs%(title)s</title>
    <style>
        body {
            font: normal 10pt "Trebuchet MS", sans-serif;
        }
        pre {
            font-size: 10pt;
            width: 89%%;
            float: left;
            margin: 0;
            padding: 0;
            overflow: auto;
        }
        #nav {
            width: 10%%;
            float: left;
            margin: 0 0 20px;
            padding: 0;
        }
        #nav li {
            list-style: none;
            margin: 0;
            padding: 2px;
        }
        a:link
            { color:#0000EE; }
        a:hover
            { color:#00A359; }
        a:visited
            { color:#551A8B; }
        a:visited:hover
            { color:#00A359; }
        a:active
            { color:#FF0000; }
        hr {
            clear: both;
        }
        #footer {
            font-style: italic;
        }
    </style>
</head>

<body>

<h1>mimefs</h1>

<p>mimefs is a networked database filesystem, implemented as an XMLRPC API. This
documentation describes that API in terms of its Python implementation.</p>

<h2>%(title)s</h2>
<ul id="nav">
%(nav)s
</ul>
<pre>
%(body)s
</pre>

<hr />

<div id="footer">
    This page was generated from the source on %(date)s.<br />
    This documentation refers to version %(version)s.<br />
    <a href="http://www.zetadev.com/">mimefs is Zeta software</a>.
</div>

</body>
"""