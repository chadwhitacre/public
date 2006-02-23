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
        out.append(self.uri)
        out.append(self.root)
        out.append(request.path)
        out.append(request.raw)

        response = httpy.Response(200)
        response.headers = {'content-type': 'text/plain'}
        response.body = '\r\n'.join(out)
        raise response

if __name__ == '__main__':
    responder = Responder()
    coupler = httpy.couplers.FastCGI(responder)
    coupler.go()
