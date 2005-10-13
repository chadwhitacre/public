import os
import sys
import threading
import urllib
from cgi import parse_qs

import rdflib

from httpy.Response import Response


whit537 = rdflib.URIRef("whit537")
eikeon = rdflib.URIRef("eikeon")
chimezie = rdflib.URIRef("chimezie")
michel = rdflib.URIRef("michel")
isA = rdflib.URIRef("http://foo/isA")


class Application:

    def __init__(self):

        # Set the Content-Type.
        # =====================
        # Browsers generally don't yet display application/rdf+xml inline.

        if os.environ['HTTPY_MODE'] == 'deployment':
            self.content_type = 'application/rdf+xml'
        else:
            self.content_type = 'text/xml'


        # Open up the database and set up a write lock.
        # =============================================
        # This will create it if necessary.

        self.store = rdflib.Graph("Sleepycat")
        self.store.open(self.fs_root)
        self.write_lock = threading.Lock()


    def respond(self, request):
        """Given a request, hand it off to a method handler.
        """
        try:
            if request.path != '/':
                response = Response(301)
                response.headers['location'] = '/'
                raise response
            handler = getattr(self, request.method, None)
            if handler:
                handler(request)
            else:
                raise Response(501) # Not Implemented
        finally:
            pass
            #self.store.close()


    def GET(self, request):

        # Parse the querystring.
        # ======================
        # We only want the first value for each argument.

        query = {}
        for k, v in parse_qs(request.uri['query'], True).items():
            query[k] = v[0]


        # Implement GET with no query.
        # ============================
        # "The simplest form of a query is a plain HTTP GET.  It returns all
        # the RDF statements in the model at that URL."
        # -- http://w3.org/Submission/2003/SUBM-rdf-netapi-20031002/#http-query

        if query == {}:
            response = Response(200)
            response.headers['Content-Type'] = self.content_type
            response.body = self.store.serialize()
            raise response


        # Implement GET with a query.
        # ===========================
        # Query implementations should take the query less lang as keyword
        # arguments.

        else:
            if 'lang' not in query:
                raise Response(400, "You must specify a query language.")

            lang = urllib.unquote(query['lang'])
            del query['lang']
            query_processor = self.get_query_processor(lang)
            if query_processor:
                query_processor(**query)
            else:
                raise Response(400, "Sorry, we don't support the " +
                                    "`%s' query language." % lang)


    def POST(self):
        """
        """


    langs = {}
    langs['http://www.semanticwebserver.com/2003/01/Query/TriplePattern'] = 'TriplePattern'

    def get_query_processor(self, lang):
        """Given a 'lang' argument, return a method of self, or None.

        lang could be a URI or a nickname. This method understands both.

        """
        if lang in self.langs:              # URI
            return getattr(self, self.langs[lang])
        elif lang in self.langs.values():   # nick
            return getattr(self, lang)
        else:
            return None


    def TriplePattern(self, subject='', predicate='', object='', literal=''):
        """Given a triple pattern, return an RDF/XML graph.
        """

        # Validate and parse incoming data.
        # =================================

        if object and literal:
            raise Response(400, "Only one of parameters 'object' or " +
                                "'literal' may be used in a single request.")

        def _parse(a):
            if a in ('', '*'):  # wildcard
                return None
            else:               # URI
                return rdflib.URIRef(urllib.unquote(a))

        s = _parse(subject)
        p = _parse(predicate)
        if literal:
            o = rdflib.Literal(literal)
        else:
            o = _parse(object)


        # Build outgoing graph and send it along.
        # =======================================

        out = rdflib.Graph("Memory")
        for statement in self.store.triples((s,p,o)):
            out.add(statement)

        response = Response(200)
        response.headers['Content-Type'] = self.content_type
        response.body = out.serialize()
        raise response
