#!/usr/bin/env python
"""astutils -- utilities for working with abstract syntax tree (AST) objects
"""
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import token, symbol
from os import linesep
from pprint import pformat
from StringIO import StringIO

def ast2read(ast):
    """Given an AST object, return a human-readable representation of the tree.

    Usage:

        >>> import parser
        >>> from astutils import ast2read
        >>> ast = parser.suite("print 'hello world'")
        >>> print ast2read(ast)
        ['file_input',
         ['stmt',
          ['simple_stmt',
           ['small_stmt',
            ['print_stmt',
             ['NAME', 'print'],
             ['test',
              ['and_test',
               ['not_test',
                ['comparison',
                 ['expr',
                  ['xor_expr',
                   ['and_expr',
                    ['shift_expr',
                     ['arith_expr',
                      ['term',
                       ['factor',
                        ['power',
                         ['atom', ['STRING', "'hello world'"]]]]]]]]]]]]]]]],
           ['NEWLINE', '']]],
         ['ENDMARKER', '']]
    """

    def walk(cst):
        """ given an AST list (a CST?), recursively walk it and replace the
        nodes with human-readable equivalents
        """

        for node in cst:
            if type(node) is type([]):
                # we have a list of subnodes; recurse
                walk(node)
            else:
                # we have an actual node; interpret it and store the result
                if type(node) is type(0):
                    if node < 256:
                        readable_node = token.tok_name[node]
                    else:
                        readable_node = symbol.sym_name[node]
                else:
                    readable_node = node

                cst[cst.index(node)] = readable_node

    TREE = ast.tolist()
    walk(TREE)
    return pformat(TREE)


def ast2text(ast):
    """Given an AST object, return an approximation of the source code that
    generated it. The approximation will only differ from the original in non-
    essential whitespace.

    Usage:

        >>> import parser
        >>> from ast2text import ast2text
        >>> ast = parser.suite("print 'hello world'")
        >>> print ast2text(ast)
        print 'hello world'

    """

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

    # trim a possible trailing newline and/or space; this is just to make the
    # doctest work
    output = TEXT.getvalue()
    if output.endswith(linesep): output = output.rstrip(linesep)
    if output.endswith(' '):  output = output[:-1]

    return output


if __name__ == "__main__":
    import doctest
    doctest.testmod()
