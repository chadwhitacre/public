################################################################################
#                                                                              #
#   TEST FRAMEWORK                                                             #
#                                                                              #
################################################################################

import os
from traceback import print_exc

class testosterone:
    """Testoterone is a manly testing framework. To use it, include it in a
    testing script. In this script, set up a bunch of fixture, and then call
    testosterone. Testosterone takes three parameters:

        block -- a multi-line string of single-line statements, empty lines,
            and comments (lines beginning with #); initial and trailing
            whitespace per line is ignored

        globals, locals -- the context in which the statements should be
            evaluated and/or executed

    Each statement is treated in sequence, according to the following rubric:

        1. If the statement is prefixed with 'exec ' or 'eval ', then the
           remainder of the line (the prefix is stripped off) is executed or
           evaluated, respectively.

        2. If there is no prefix, then the statement is first assumed to be a
           test expression evaluation is attempted. If this succeeds, then the
           evaluated value is interpreted as a pass/fail for that test.

        3. If evaluation raises SyntaxError, then the statement is assumed to
           be an executable statement and is executed.

        4. All otherwise uncaught exceptions result in the test being tallied as
           an exception.

    If a an executable statement begins with 'print' or 'pprint' then the output
    is wrapped to be more readable.

    Statements that successfully execute are not counted towards total tests.

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
                # explicit
                if statement.startswith('exec '):
                    statement = statement[5:].strip()
                    self.do_exec(statement)
                elif statement.startswith('eval '):
                    statement = statement[5:].strip()
                    self.do_eval(statement)

                # implicit
                else:
                    try:
                        self.do_eval(statement)
                    except SyntaxError:
                        self.do_exec(statement)
            except:
                self.do_except(statement)

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
        """given a statement, evaluate it and tally/output the result
        """
        if eval(statement, self.globals, self.locals):
            self.passed += 1
        else:
            print 'False: %s ' % statement
            self.failed += 1

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
        """given a bad statement, tally and output the exception
        """
        print
        print statement
        print_exc()
        print
        self.exceptions += 1
