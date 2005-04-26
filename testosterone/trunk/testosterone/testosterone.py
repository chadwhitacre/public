################################################################################
#                                                                              #
#   TEST FRAMEWORK                                                             #
#                                                                              #
################################################################################

import os
from traceback import print_exc

class testosterone:
    """Testoterone is a simple testing framework. To use it, include it in a
    testing script. In this script, set up a bunch of fixture, and then call
    testosterone. Testosterone takes three parameters:

      block -- a multi-line string of single-line statements, empty lines,
      and comments (lines beginning with #); initial and trailing whitespace per
      line is ignored

      globals, locals -- the context in which the statements should be evaluated
      and possibly executed

    Each statement is treated in sequence: first it is assumed to be a test
    expression and is evaluated. If this succeeds, then the evaluated value is
    interpreted as a pass/fail for that test. If evaluation raises a
    SyntaxError, then the statement is assumed to be an executable statement and
    is executed. This allows for changing the fixture during test runtime, as
    well as printing during runtime. If execution also raises an exception, then
    the test is tallied as an exception.
    """

    passed = 0
    failed = 0
    exceptions = 0

    def __init__(self, block, globals, locals):
        block = [a.strip() for a in block.split(os.linesep)]
        block = [a for a in block if a.strip()]
        self.statements = [a for a in block if not a.startswith('#')]

        self.globals = globals
        self.locals = locals

        self.do_header()
        self.do_body()
        self.do_footer()

    ##
    # presentation
    ##

    def do_header(self):
        """output a header for the report
        """
        print
        print "#"*79
        print "#"+"running tests ...".rjust(47)+" "*30+"#"
        print "#"*79
        print

    def do_body(self):
        """run the tests and output the body of the report
        """
        for statement in self.statements:

            try:
                if statement.startswith('exec '):
                    # statement is explicitly executable
                    statement = statement[5:].strip()
                    self.do_exec(statement)
                else:
                    self.do_eval(statement)
            except:
                self.do_exec(statement)

    def do_footer(self):
        """output a footer for the report
        """

        total = self.passed + self.failed + self.exceptions
        if self.failed + self.exceptions: print

        print """\
#######################
#       RESULTS       #
#######################
#                     #
#       passed: %s  #
#       failed: %s  #
#   exceptions: %s  #
# ------------------- #
#  total tests: %s  #
#                     #
#######################
""" % ( str(self.passed).rjust(4)
      , str(self.failed).rjust(4)
      , str(self.exceptions).rjust(4)
      , str(total).rjust(4))


    ##
    # logic
    ##

    def do_eval(self, statement):
        """given a statement, try to evaluate it; on SyntaxError, execute it
        """
        try:
            if eval(statement, self.globals, self.locals):
                self.passed += 1
            else:
                print 'False: %s ' % statement
                self.failed += 1
        except SyntaxError:
            do_exec(statement)

    def do_exec(self, statement):
        """given a statement, execute it; if a print statement, wrap its output
        """
        printing = statement.startswith('print') or\
                   statement.startswith('pprint')
        if printing:
            print
            print statement
            print '-'*79
        exec statement in self.globals, self.locals
        if printing: print

    def do_except(self, statement):
        """given a bad statement, capture its exception
        """
        print
        print statement
        print_exc()
        print
        self.exceptions += 1
