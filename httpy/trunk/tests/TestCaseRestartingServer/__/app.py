"""This httpy application is for testing the RestartingServer.

When an app drops into the post-mortem debugger, and then the server restarts,
the terminal gets screwed up -- I believe that stdin is lost somehow.

This is an attempt to isolate the problem. The idea is that you would run httpy
over this application. This is easier than adding RestartingServer to
TestCaseHttpy. :-)

Here are the specific steps to follow:

    1. start serving this site with httpy in development mode
    2. hit it TTW -- you should see "Greetings, program! [1]"
    3. uncomment the StandardError in Application.respond
    4. save the file -- you should see httpy restart
    5. hit it TTW -- you should see a (Pdb) prompt
    6. type 'list' <enter> -- you should be able to see what you are typing
    7. change something trivial in this file and save it -- you should see
       httpy restart in the middle of the (Pdb) prompt
    8. hit it TTW -- you should see another (Pdb) prompt
    9. try typing 'list' <enter> at the prompt -- the current bug is that you
       can't see what you're typing.

"""

import os

from httpy.Response import Response


class Application:

    i = 0

    def respond(self, request):
        self.i += 1
        raise StandardError("foo!")
        raise Response( 200
                      , "Greetings, program! [%d]" % self.i
                      , {'content-type':'text/plain'}
                       )
