#!/usr/bin/env python
"""Dumb little test script.
"""

# Make sure we can find ourselves.
# ================================

import os, sys
path = os.path.realpath('../site-packages/')
sys.path.insert(0, path)


# Go for it!
# ==========

import httpy

class Responder:
    def respond(self, request):
        out = []
        out.append(request.path)
        out.append(request.path.info or '')
        out.append(request.path.translated or '')

        response = httpy.Response(200)
        response.headers = {'content-type': 'text/plain'}
        response.body = '\r\n'.join(out)
        raise response

if __name__ == '__main__':
    responder = Responder()
    coupler = httpy.couplers.CGI(responder)
    coupler.go()
