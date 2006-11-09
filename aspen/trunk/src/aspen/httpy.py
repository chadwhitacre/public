#!/usr/bin/env python
"""WSGI middleware to allow returning a string or Response object.

The request side of WSGI--the "commons" of the environ mapping--is quite
nice. It honors the tradition of CGI, and it's just a mapping. Simple.

The response-side API is a little stiffer, because WSGI has to support edge
cases like serving large files, complex exception handling, and HTTP/1.1
features. This results in warts like start_response, and the requirement
that apps return an iterable. The intention is that these warts be smoothed
over at other layers, and that's what we're doing here.

Apps below this shim may speak plain WSGI, but they may also return a
string, which will be sent back as text/html. They may also return or raise
a Response object.

"""
import BaseHTTPServer
from email.Message import Message


__author__ = "Chad Whitacre <chad@zetaweb.com>"
__version__ = "1.0"
__all__ = ('Response', 'Responder')


_responses = BaseHTTPServer.BaseHTTPRequestHandler.responses


class Response(StandardError):
    """Represent an HTTP Response message.
    """

    def __init__(self, code=200, body='', headers=None):
        """Takes an int, a string, and a dict.

            - code        an HTTP response code, e.g., 404
            - body        the message body as a string
            - headers     a dictionary of HTTP headers (or list of tuples)

        Body is second because one more often wants to specify a body without
        headers, than a header without a body.

        """
        if not isinstance(code, int):
            raise TypeError("'code' must be an integer")
        elif not isinstance(body, basestring):
            raise TypeError("'body' must be a string")
        elif headers is not None and not isinstance(headers, (dict, list)):
            raise TypeError("'headers' must be a dictionary or a list of " +
                            "2-tuples")

        StandardError.__init__(self)
        self.code = code
        self.body = body
        self.headers = Message()
        if headers:
            if isinstance(headers, dict):
                headers = headers.items()
            for k, v in headers:
                self.headers[k] = v


    def __repr__(self):
        return "<Response: %s>" % str(self)

    def __str__(self):
        return "%d %s" % (self.code, self.status_msg()[0])

    def status_msg(self):
        return _responses.get(self.code, ('???','Unknown HTTP status'))


    def to_wsgi(self, start_response):
        """Convert ourselves to a WSGI response.

        XXX: WSGI exception handling?

        """
        response = self.status_msg()

        status = "%d %s" % (self.code, response[0])
        headers = [(str(k), str(v)) for k,v in self.headers.items()]
        body = [self.body and self.body or response[1]]

        start_response(status, headers)
        return body


class Responder(object):
    """WSGI middleware to also allow returning a string or Response object.
    """

    def __init__(self, app):
        self.wrapped_app = app

    def __call__(self, environ, start_response):
        try:
            response = self.wrapped_app(environ, start_response)
        except Response, response:
            pass
        except:
            raise

        if isinstance(response, Response):
            response = response.to_wsgi(start_response)
        elif isinstance(response, basestring):
            response = Response(200, response)
            response.headers['Content-Type'] = 'text/html'
            response = response.to_wsgi(start_response)

        return response


if __name__ == '__main__':
    """Simple smoke test.

    Hit http://localhost:8080/ in a web browser after running this script. Only
    one of the calls to Server can be uncommented or you'll get:

      socket.error: (48, 'Address already in use')

    """
    from wsgiref.simple_server import make_server # included w/ Python 2.5

    Server = lambda app: make_server('', 8080, app)
    app = lambda e, s: "Greetings, program!"

    def app2(environ, start_response):
        return Response( 200, "Greetings, program!"
                       , {'Content-Type':'text/plain'}
                        )

    server = Server(Responder(app)) # tests returning a string
    #server = Server(Responder(app2)) # tests returning a Response
    #server = Server(app) # unwrapped; raises AssertionError when hit

    server.serve_forever()
