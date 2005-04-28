#!/usr/bin/env python
"""ASTutils -- utilities for working with abstract syntax tree (AST) objects
"""
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

__author__ = 'Chad Whitacre'
__version__ = '0.1'

import parser, token, symbol
from os import linesep
from pprint import pformat
from StringIO import StringIO

class ASTutilsException(Exception):
    pass

class ASTutils:
    """A class holding utilities for working with syntax trees. Where an st
    argument is called for, this may be either an AST object, or a list or tuple
    as produced by parser.ast2list and parser.ast2tuple. """


    def _standardize_st(self, st, format='tuple'):
        """Given a syntax tree and a desired format, return the tree in that
        format.
        """
        # convert the incoming ast/cst into an AST
        if type(st) is type(parser.suite('')):
            ast = st
        else:
            if type(st) in (type(()), type([])):
                ast = parser.sequence2ast(st)
            else:
                raise ASTutilsException, "incoming type unrecognized: " +\
                                         repr(type(st))

        # return the tree in the desired format
        formats = { 'tuple' : ast.totuple
                  , 'list'  : ast.tolist
                  , 'ast'   : lambda: ast
                   }

        outgoing = formats.get(format.lower())
        if outgoing is None:
            raise ASTutilsException, "requested format unrecognized: " + format

        return outgoing()

    _standardize_st = classmethod(_standardize_st)



    def ast2read(self, st):
        """Given a syntax tree, return a more human-readable representation of
        the tree than is returned by parser.ast2list and parser.ast2tuple.

        Usage:

        >>> import parser
        >>> ast = parser.suite("print 'hello world'")
        >>> print ASTutils.ast2read(ast)
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

        # define our recursive function
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

        # ggg!
        TREE = self._standardize_st(st, 'list')
        walk(TREE)
        return pformat(TREE)

    ast2read = classmethod(ast2read)



    def ast2text(self, st):
        """Given a syntax tree, return an approximation of the source code that
        generated it. The approximation will only differ from the original in
        non-essential whitespace and missing comments.

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

        # trim a possible trailing newline and/or space; this is necessary to
        # make the doctest work

        output = TEXT.getvalue()
        if output.endswith(linesep): output = output.rstrip(linesep)
        if output.endswith(' '):  output = output[:-1]

        return output

    ast2text = classmethod(ast2text)



    def promote_stmt(self, cst):
        """Given a cst stmt fragment (list or tuple), return a first-class cst.

        Usage:

            #>>> import parser
            #>>> block = "if 1: print 'hello world'"
            #>>> ast = parser.suite(block)
            #>>> ASTutils.hasnode(ast, 'suite')
            #True
            #>>> suite = ASTutils.getnode(ast, 'suite')
            #>>> print suite

            #>>> stmt = ASTutils.getnode(suite, 'stmt')
            #>>> print stmt
            #>>> st = ASTutils.promote_stmt(stmt)
            #>>> print st

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

    promote_stmt = classmethod(promote_stmt)



    def getnode(self, st, nodetype):
        """Given an AST object or a cst fragment (as list or tuple), and a
        string or int nodetype, return the first instance of the desired
        nodetype as a cst fragment, or None if the nodetype is not found.

        Usage:

            >>> import parser, symbol
            >>> ast = parser.suite("print 'hello world'")
            >>> ASTutils.getnode(ast, 'print_stmt')
            (271, (1, 'print'), (298, (299, (300, (301, (303, (304, (305, (306, (307, (308, (309, (310, (311, (3, "'hello world'")))))))))))))))
            >>> ASTutils.getnode(ast, symbol.pass_stmt) is None
            True
            >>> ASTutils.getnode(ast, -1) # bad data
            Traceback (most recent call last):
                ...
            ASTutilsException: nodetype '-1' is not in symbol or token tables

        """

        cst = self._standardize_st(st, 'tuple')

        # standardize the incoming nodetype to a symbol or token int
        if type(nodetype) is type(''):
            symtype = getattr(symbol, nodetype, '')
            if symtype:
                nodetype = symtype
            else:
                toktype = getattr(token, nodetype, '')
                if toktype:
                    nodetype = toktype
                else:
                    nodetype = -1 # bad data

        # validate the input
        valid_ints = symbol.sym_name.keys() + token.tok_name.keys()
        if nodetype not in valid_ints:
            raise ASTutilsException, "nodetype '%s' " % nodetype +\
                                     "is not in symbol or token tables"

        # define our recursive function
        def walk(cst, nodetype):
            for node in cst:
                if type(node) is type(()):
                    candidate = walk(node, nodetype)
                else:
                    candidate = cst
                if candidate is not None:
                    if candidate[0] == nodetype:
                        return candidate
            return None # default

        # ggg!
        return walk(cst, nodetype)

    getnode = classmethod(getnode)



    def hasnode(self, cst, nodetype):
        """Given an AST object or a cst fragment (either in list or tuple form),
       and a nodetype (either as a string or an int), return a boolean.

        Usage:

            >>> import parser, symbol
            >>> ast = parser.suite("print 'hello world'")
            >>> ASTutils.hasnode(ast, 'print_stmt')
            True
            >>> ast = parser.suite("if 1: print 'hello world'")
            >>> ASTutils.hasnode(ast, 'print_stmt')
            True

        """
        return self.getnode(cst, nodetype) is not None

    hasnode = classmethod(hasnode)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
