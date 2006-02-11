#!/usr/bin/env python
"""This is a test runner for the httpy library.

Usage, e.g.:

    $ python bin/test.py site-packages/httpy/couplers

The argument to test.py is a path constraint. This runner looks for all tests/
directories under the path constraint, recursing into subdirectories. Within
those directories, it looks for files named test_*.py, and adds the return value
of test_suite within those files to its list of tests to run.

This really wants to have a RestartingTester that behaves like RestartingServer.
In fact, our test-finding code is very similar to our responder locating code in
the Multiple responder.


curses app

screen 1: all tests
    tests should be hierarchical
    should be able to choose a point on the tree
    the tree should keep itself up-to-date
        once per loop, walk tree and refresh tree ... too much?

screen 2: multiple tests chosen
    shows stats at the top
    lists tests with failure/error output
    can key into specific tests

screen 3: single test
    shows stats at the top
    shows output from single test
    if we came from screen 2, should be able to get back there


Tests themselves should be run in a separate process that calls the same runner
in non-interactive mode. Spawning a new process on each "request" means we don't
have to worry about tracking module changes and restarting. We can just track
filesystem changes and rerun the module. After noticing a fs change, we should
wait a second or two in case any other quick changes happen (2 files saved, e.g.)


so how to build this up:
    non-interactive mode first





"""
import curses
import getopt
import os
import sys


class Test537:

    def __init__(self):
        pass

    def interact(self):
        def foo(stdscr):
            stdscr.bkgdset(' ')
            stdscr.border()
            stdscr.refresh()
            try:
                while 1:
                    pass
            except KeyboardInterrupt:
                pass
        curses.wrapper(foo)
        os.system('clear')


    def tree(self, name):
        """Given a starting point, find all test cases.

        A tree of names that can be passed to loadTestsFromModule[s]

        we either generate a tree from the filesystem or from module-space

        """

        if '.' in name:
            raise StandardError("can't take dotted names yet")

        module = __import__(name)
        path = os.path.dirname(module.__file__)
        modules = []
        for mod in sys.modules:
            if mod.startswith(name):
                obj = sys.modules[mod]
                if obj is None:
                    continue
                if obj.__file__.startswith(path):
                    modules.append(mod)
        modules.sort()
        for mod in modules:
            print mod



test537 = Test537()

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hi", ["help", "interactive"])
        except getopt.error, msg:
            raise Usage(msg)

        name = ''
        if args:
            name = args[0]

        method = test537.tree
        for opt in opts:
            if opt in ('-i', '--interactive'):
                method = test537.interact

        method(name)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2


if __name__ == "__main__":
    sys.exit(main())



