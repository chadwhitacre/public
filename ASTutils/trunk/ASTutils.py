#!/usr/bin/env python
"""ASTutils -- utilities for working with abstract syntax tree (AST) objects
"""
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import parser, token, symbol
from os import linesep
from pprint import pformat
from StringIO import StringIO


class ASTutilsException(Exception):
    pass


class ASTutils:

    def ast2read(ast):
        """Given an AST object, return a human-readable representation of the
        tree.

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

        self.

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

    ast2read = staticmethod(ast2read)


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
                        if not node.startswith('#'):
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

        # trim a possible trailing newline and/or space; this is necessary to make the
        # doctest work
        output = TEXT.getvalue()
        if output.endswith(linesep): output = output.rstrip(linesep)
        if output.endswith(' '):  output = output[:-1]

        return output

    ast2text = staticmethod(ast2text)


    def promotenode(cst):
        """Given a cst stmt fragment (list or tuple), return a first-class cst.
        """
        if type(cst) in (type(()), type([])):
            if cst[0] == symbol.stmt:
                if type(cst) is type(()):
                    return ( symbol.file_input
                           , cst
                           , (token.NEWLINE, '')
                           , (token.ENDMARKER,'')
                            )
                elif type(cst) is type([]):
                    return [ symbol.file_input
                           , cst
                           , [token.NEWLINE, '']
                           , [token.ENDMARKER,'']
                            ]
            else:
                raise ASTutilsException, "only stmt's can be promoted"
        else:
            raise ASTutilsException, "cst to promote must be list or tuple"


    def getnode(cst, nodetype):
        """Given an AST object or a cst fragment (as list or tuple), and a string
        or int nodetype, return the first instance of the desired nodetype as a cst
        fragment, or None if the nodetype is not found.

        Usage:

            >>> import parser
            >>> from astutils import getnode
            >>> ast = parser.suite("print 'hello world'")
            >>> getnode(ast, 'print_stmt')

        """

        # convert the incoming ast/cst into a first-class cst tuple
        ast = parser.suite('')
        if type(cst) is type(ast):
            cst = cst.totuple()
        else:
            if cst[0] not in ( symbol.single_input
                             , symbol.file_input
                             , symbol.eval_input ):
                # convert a fragment to a first-class cst so we can parse it
                cst = promotenode(cst)
        if type(cst) is type([]):
            cst = parser.sequence2ast(cst).totuple()

        # convert the incoming nodetype to a symbol or token int
        if type(nodetype) is type(''):
            symtype = getattr(symbol, nodetype, '')
            if symtype:
                nodetype = symtype
            else:
                toktype = getattr(token, nodetype, '')
                if toktype:
                    nodetype = toktype
                else:
                    raise ASTutilsException, "nodetype '%s' " % nodetype +\
                                             "is not in symbol or token tables"

        # define our recursive function
        def walk(cst, nodetype):
            for node in cst:
                if type(node) is type(()):
                    return walk(node, nodetype)
                else:
                    if node == nodetype:
                        return cst
            return None

        return walk(cst, nodetype)


    def hasnode(cst, nodetype):
        """Given an AST object or a cst fragment (either in list or tuple form), and
        a nodetype (either as a string or an int), return a boolean.

        Usage:

            >>> import parser
            >>> from astutils import hasnode
            >>> ast = parser.suite("print 'hello world'")
            >>> hasnode(ast, 'print_stmt')
            True
            >>> hasnode(ast, 273) # pass_stmt
            False
            >>> hasnode(ast.tolist(), 'print_stmt')
            True
            >>> hasnode(ast.totuple(), 273)
            False

            #>>> hasnode(ast, 'foo_stmt') # bad nodetype
            #<traceback>
            #>>> hasnode(ast, 1500) # bad nodetype
            #<traceback>

        """
        return getnode(cst, nodetype) is not None




if __name__ == "__main__":
    import doctest
    doctest.testmod()
