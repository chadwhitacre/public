#!/usr/bin/env python
"""This module defines the Observer class.
"""

import linecache
import parser
import sys
import symbol
import time
import token
import traceback
from StringIO import StringIO

from pytest.ASTutils import ASTutils

class Observer(StringIO):
    """This class executes, monitors, and reports on the execution of a pytest.
    """

    passes = 0
    failures = 0
    exceptions = 0

    nontest_excs = 0

    stopwatch = None


    ##
    # main callables
    ##

    def run(self, filename, interpolated, globals, locals):
        """run the interpolated test script; if that fails, run the original
        script so that the traceback is accurate
        """

        # save this for a default header for our report
        self.filename = filename

        try:
            exec interpolated in globals, locals
        except:
            try:
                execfile(filename, globals, locals)
            except:
                linenumber = sys.exc_info()[2].tb_next.tb_lineno
                statement = linecache.getline(filename, linenumber)
                statement = statement.strip().split("#")[0]

                self.print_h2('Crisis', statement, linenumber)
                traceback.print_exc(file=self)
                print
                self.print_h2('', 'TEST TERMINATED', -1)
                print
                self.nontest_excs += 1

    def intercept(self, statement, linenumber, globals, locals,
                  COMPARING=False, PRINTING=False):
        """Given a statement, some context, and a couple optional flags, write
        to our report. Since we are called from inside of the test, sys.stdout
        is actually our parent. However, we leave sys.stderr alone, and any
        exceptions in fixture will raise as normal.
        """

        if COMPARING:
            try:
                if eval(statement, globals, locals):
                    self.passes += 1
                else:
                    self.print_h2('Failure', statement, linenumber)
                    ast = parser.expr(statement)
                    for term in ASTutils.getnodes(ast, 'expr'):
                        tast = parser.sequence2ast(self._expr2eval_input(term))
                        text = ASTutils.ast2text(tast)
                        evaled = str(eval(text, globals, locals))
                        if text <> evaled:
                            self.print_h3(text, evaled)
                    print
                    print
                    self.failures += 1
            except:
                self.print_h2('Exception', statement, linenumber)
                traceback.print_exc(file=self)
                print
                print
                self.exceptions += 1

        elif PRINTING:
            self.print_h2('More Info', statement, linenumber)
            try:
                exec statement in globals, locals
            except:
                traceback.print_exc(file=self)
                self.nontest_excs += 1
            print
            print


    ##
    # stopwatch
    ##

    def start_timer(self):
        self.stopwatch = time.time()

    def stop_timer(self):
        self.stopwatch = time.time() - self.stopwatch



    ##
    # report generation
    ##

    def report(self, heading=''):

        if not heading:
            heading = self.filename # this assumes we've been run

        self.print_summary(heading)
        print self.getvalue()
        self.print_summary(heading)

    def print_summary(self, heading):
        """output a header for the report
        """
        total = self.passes + self.failures + self.exceptions
        summary_data = {}
        summary_data['total']       = str(total).rjust(4)
        summary_data['passes']      = str(self.passes).rjust(4)
        summary_data['failures']    = str(self.failures).rjust(4)
        summary_data['exceptions']  = str(self.exceptions).rjust(4)
        summary_data['nontest_excs']  = str(self.nontest_excs).rjust(4)
        summary_data['seconds']     = ('%.1f' % self.stopwatch).rjust(6)

        summary_list = [
            "           passes: %(passes)s    ",
            "         failures: %(failures)s    ",
            "       exceptions: %(exceptions)s    ",
            "    ---------------------- ",
            "      total tests: %(total)s    ",
            "                           ",
            " other exceptions: %(nontest_excs)s    ",
            "                           ",
            "     time elapsed: %(seconds)ss "


                        ]
        summary_list = [l % summary_data for l in summary_list]

        self.print_h1(heading)
        print '#%s#' % (' '*78,)
        for line in summary_list:
            print '# %s #' % self._center(line, 76)
        print '#%s#' % (' '*78,)
        print '#'*80
        print



    ##
    # formatting helpers
    ##

    def print_h1(self, h):
        if len(h) >= 73:
            h = h[:73] + '...'
        print "#"*80
        print "# %s #" % self._center(h, 76)
        print "#"*80

    def print_h2(self, stype, h, lnum):
        if len(h) >= 49:
            h = h[:49] + '...'

        if lnum <> -1:
            linenumber = "LINE: %s" % str(lnum).rjust(4)
        else:
            linenumber = "          "

        print '+' + '-'*78 + '+'
        print '| %s  %s  %s |' % ( stype.upper().ljust(10)
                                 , self._center(h, 52)
                                 , linenumber
                                  )
        print '+' + '-'*78 + '+'
        print

    def print_h3(self, h, b):
        """given a heading and a body, output them
        """
        if len(h) >= 73:
            h = h[:73] + '...'

        print h
        print '-'*80
        print b
        print

    def _center(self, s, i):
        """given a string s and an int i, return a string i chars long with s
        centered
        """
        slen = len(s)
        rpadding = (i - slen) / 2
        lpadding = rpadding + ((i - slen) % 2)
        return ' '*rpadding + s + ' '*lpadding

    def _expr2eval_input(self, expr):
        """given an expr as a list, promote it to an eval_input
        """
        return [symbol.eval_input,[symbol.testlist,[symbol.test,
                [symbol.and_test,[symbol.not_test,[symbol.comparison,
                 expr]]]]],[token.NEWLINE, ''],[token.ENDMARKER, '']]


if __name__ == '__main__':
    import doctest
    doctest.testmod()
