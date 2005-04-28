#!/usr/bin/env python
"""Given an abstract syntax tree (AST) object, return an approximation of
the source code that generated it. The approximation will only differ from
the original in non-essential whitespace.

Usage:

    >>> import parser
    >>> from ast2text import ast2text
    >>> ast = parser.suite("print 'hello world'")
    >>> print ast2text(ast)
    print 'hello world'

"""
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import token
from os import linesep
from StringIO import StringIO

def ast2text(ast):

    def walk(cst, TEXT):
        """ given an AST tuple (a CST?), recursively walk it and assemble the
        nodes back into a text code block
        """

        for node in cst:
            if type(node) is type(()):
                # we have a tuple of subnodes; recurse
                walk(node, TEXT)
            else:
                # we have an actual node; interpret it and store the result
                if type(node) is type(''):
                    if node <> '': node += ' ' # insert some whitespace
                    text = node
                elif node == token.NEWLINE:
                    text = '\n'
                elif node == token.INDENT:
                    text = '    '
                else:
                    text = ''

                TEXT.write(text)

    TEXT = StringIO()
    walk(ast.totuple(), TEXT)

    # trim a trailing newline and (possibly) space; this is just to make the
    # doctest work
    output = TEXT.getvalue()
    if output.endswith(linesep): output = output.rstrip(linesep)
    if output.endswith(' '):  output = output[:-1]

    return output


if __name__ == "__main__":
    import doctest
    doctest.testmod()
