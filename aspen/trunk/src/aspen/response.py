import BaseHTTPServer
from email.Message import Message


__all__ = ('Response',)
responses = BaseHTTPServer.BaseHTTPRequestHandler.responses


class Response(StandardError):
    """An HTTP Response message.

    All WSGI apps below aspen may raise or return an instance of this class, and
    Website will call to_wsgi.

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
        return "%d %s" % (self.code, self.response()[0])

    def response(self):
        return responses.get(self.code, ('???','Unknown HTTP status'))


    def to_wsgi(self, start_response):
        """Convert ourselves to a WSGI response.

        XXX: WSGI exception handling

        """
        response = self.response()

        status = "%d %s" % (self.code, response[0])
        headers = [(unicode(k),unicode(v)) for k,v in self.headers.items()]
        body = [self.body and self.body or response[1]]

        start_response(status, headers)
        return body
