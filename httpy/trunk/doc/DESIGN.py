Here is the entire request handling process, represented in pseudocode


# Request Comprehension
# =====================

    There are two or three parts to every Request: Request-line, headers, body

    read the Request-Line into method, uri, abs_path, querystring, and version
    read the headers into headers
    read any message body into body
      if Content-Length and not Transfer-Encoding:
          stream.read(Content-Length)
      elif Transfer-Encoding:
          http://www.w3.org/Protocols/rfc2616/rfc2616-sec19.html#sec19.4.6
      else:
          raise

    class Request:
        """An HTTP Request message.

            http://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html

        """

        def __init__(self, stream):
            """Takes an incoming HTTP stream.
            """
            self.parse_line(stream)
            self.parse_headers(stream)
            self.parse_body(stream)

        def parse_line(self, stream):
            pass

        def parse_headers(self, stream):
            pass

        def parse_body(self, stream):
            pass



# State
# =====

    class Transaction(dict):
        """A single transaction within an application.
        """

        def __init__(self, request):
            """Takes an httpy.Request object.
            """
            self.request = request
            self.query = cgi.parse_qs(request.querystring)
            self.cookie = Cookie.SimpleCookie(request.headers.get('Cookie','')
            self.post = self.parse_post(request.body)
            self.__dict__ = self.harmonize()

        def process(self):
            self.response = Response()

        def end(self, response):
            """Given an httpy.Response, initiate the end of the transaction.
            """
            raise StatusCodes.OK(response)



# Response
# ========

    class Response:
        """An HTTP Response message.

            http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html

        """

        def __init__(self, state):
            """Takes an httpy.Transaction.
            """
            self.state = state
            self.request = state.request
