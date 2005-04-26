################################################################################
#                                                                              #
#   TEST FRAMEWORK                                                             #
#                                                                              #
################################################################################

import os
from traceback import print_exc

def testosterone(block, globals, locals):

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

    block = [a.strip() for a in block.split(os.linesep)]
    block = [a for a in block if a.strip()]
    statements = [a for a in block if not a.startswith('#')]

    passed = 0; failed = 0; exceptions = 0

    print
    print "#"*79
    print "#"+"running tests ...".rjust(47)+" "*30+"#"
    print "#"*79
    print

    for statement in statements:

        # first we try to evaluate it as a conditional expression statement
        # then we try to execute it
        # then we let the error ride

        try:
            try:
                if eval(statement, globals, locals):
                    passed += 1
                else:
                    print 'False: %s ' % statement
                    failed += 1
            except SyntaxError:
                print
                print statement
                print '-'*79
                exec statement in globals, locals
                print
        except:
            print
            print statement
            print_exc()
            print
            exceptions += 1

    if failed + exceptions: print

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
""" % ( str(passed).rjust(4)
      , str(failed).rjust(4)
      , str(exceptions).rjust(4)
      , str(passed + failed + exceptions).rjust(4))
