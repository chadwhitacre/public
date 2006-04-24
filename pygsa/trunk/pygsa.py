#!/usr/bin/env python

import getopt
import httplib
import sys
import urllib
from xml.sax import handler, parseString


class Result:
    """Represent a single search result.
    """
    title = ''
    url = ''
    snippet = None


class Results(handler.ContentHandler):
    """Represent a sequence of search results.
    """

    _results = None # a list of Result objects
    _curel = '' # the element currently being processed

    def __init__(self, raw):
        handler.ContentHandler.__init__(self)
        self._results = []
        parseString(raw, self)


    # Container emulation
    # ===================

    def __iter__(self):
        return self._results.__iter__()

    def next(self):
        yield self._results.next()


    # SAX API
    # =======

    def startElement(self, name, attrs):
        """
        """
        if name == 'R':
            result = Result()
            result.title = []
            result.url = []
            result.snippet = []
            # result.index = attrs...
            self._results.append(result)
        else:
            self.curel = name

    def endElement(self, name):
        """Concatenate values to a single string.
        """
        if self._results and (name == 'R'):
            result = self._results[-1]
            result.title = ''.join(result.title)
            result.url = ''.join(result.url)
            result.snippet = ''.join(result.snippet)

    def characters(self, content):
        """We don't always receive all content at once, so we build lists.
        """
        if not self._results:
            return
        result = self._results[-1]
        if self.curel == 'U':       # URL
            result.url.append(content)
            result.title.append(content)
        elif self.curel == 'T':     # title (defaults to URL)
            result.title.append(content)
        elif self.curel == 'S':     # snippet
            result.snippet.append(content)


class GoogleSearchAppliance:
    """Represent a server exposing the Google Search Appliance API.
    """

    def __init__(self, host, port=80):
        self.host = host
        self.port = port

    def __call__(self, query):
        query = urllib.quote_plus(query)
        conn = httplib.HTTPConnection(self.host, self.port)
        conn.request('GET', ( '/search?q=%s'
                            + '&output=xml_no_dtd'
                            + '&client=base'
                            + '&site=base'
                            + '&restrict='
                             ) % query)
        raw = conn.getresponse().read()
        results = Results(raw)
        conn.close()
        return results


def main(argv=None):

    if argv is None:
        argv = sys.argv
    argv = argv[1:]


    # Must specify a host[:port], and a query.
    # ========================================

    if not argv:
        print "You must specify a host[:port]."
        raise SystemExit(2)
    loc = argv[0]
    del argv[0]
    if ':' in loc:
        host, port = loc.split(':')
    else:
        host = loc
        port = 80

    if not argv:
        print "No query specified."
        raise SystemExit(2)
    else:
        query = ' '.join(argv)


    # Print results.
    # ==============

    gsa = GoogleSearchAppliance(host, port)
    results = gsa(query)
    for result in results:
        print 'title:   ' + result.title
        print 'url:     ' + result.url
        print 'snippet: ' + result.snippet
        print


if __name__ == '__main__':
    main()
