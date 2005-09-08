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




Notes

I don't care what language httpy is written in, or if it is compiled or
interpreted. I am much more concerned about:

    the API it exposes to the site developer
    ease of installation (on Win though?)
    speed/robustness


The Stack

    TOP

        9. style (CSS)
        8. client-side logic (ECMAScript)
        7. media (JPEG, Flash, etc.)
        6. markup (XHTML)

        5. response marshalling
            cookies
            sessioning
            headers
            body

        4. applications
            specific apps:
                conversation (forums, discussion mailing lists)
                distribution lists (announcement lists)
                content streams (blog, news)
                CMS (end-user-managed publications)
                catalog (i.e., gallery/album)
                commerce ( = catalog/calendar + credit cards)
                calendar
                search
                *publication -- serving a tree of files
            general application needs
                data storage/persistence
                workflow
                security
                user/group management
                versioning
                staging
                error handling
                templating (TAL)
                client-server communication
                user interface
                    browse
                        navigation -- e.g. tree, breadcrumbs, sitemap
                        orderable containers
                    find


        3. request comprehension -- translate a raw request into an object
            querystring
            headers
            cookies
            post body
            sessions

        2. application protocol (HTTP)
        1. transport protocol (TCP/IP)

    BOTTOM


httpy uses stdlib tools for #1
httpy implements #2 directly
    shooting for unconditional compliance
    checking out Co-Advisor
httpy provides stub request/response implementations
httpy provides a basic publication application
    simply serves static content from the filesystem


http errata:
    ust not
    self- elimiting
    ransfer-length
    can arse it
    varriant
    is not be construed
    section 5.1.1 of RFC 2046


Ok, now we are talking about several components:

    httpy -- uncomplicated Python webserver
        unconditionally compliant with HTTP/1.1 (Co-Advisor?)
        gives you hooks
            __/hook.py
            __/site-packages -- prepended to sys.path if present


    httpy
    httpy.Configurator
    httpy.Request
    httpy.Response
    httpy.Server
    httpy.StatusCodes

    flynn -- toolkit on top of httpy

        flynn.site
            __/frame.pt
            __/error.pt
            __/context.py
            __/apps
            foo-app/__init__.py
        flynn.http
            Request
            Response
            StatusCodes
        flynn.tron
            security program; ideal: kerberos ticket auth
        flynn.utils
            Configurator?
                harmonizes input from defaults, env, file, opts
            Navigator
