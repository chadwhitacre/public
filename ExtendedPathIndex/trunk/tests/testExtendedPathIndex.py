##############################################################################
#
# Copyright (c) 2004 Zope Corporation, Plone Solutions
# and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from ExtendedPathIndexTestCase import PathIndexTestCase, ExtendedPathIndexTestCase

from dummy import Dummy

class TestPathIndex( PathIndexTestCase ):
    """ Test ExtendedPathIndex objects """

    def testEmpty(self):
        self.assertEqual(self._index.numObjects() ,0)
        self.assertEqual(self._index.getEntryForObject(1234), None)
        self._index.unindex_object( 1234 ) # nothrow
        self.assertEqual(self._index._apply_index({"suxpath":"xxx"}), None)

    def testUnIndex(self):
        self._populateIndex()
        self.assertEqual(self._index.numObjects(), 18)

        for k in self._values.keys():
            self._index.unindex_object(k)

        self.assertEqual(self._index.numObjects(), 0)
        self.assertEqual(len(self._index._index), 0)
        self.assertEqual(len(self._index._unindex), 0)

    def testReindex(self):
        self._populateIndex()
        self.assertEqual(self._index.numObjects(), 18)

        o = Dummy('/foo/bar')
        self._index.index_object(19, o)
        self.assertEqual(self._index.numObjects(), 19)
        self._index.index_object(19, o)
        self.assertEqual(self._index.numObjects(), 19)


    def testUnIndexError(self):
        self._populateIndex()
        # this should not raise an error
        self._index.unindex_object(-1)

        # nor should this
        self._index._unindex[1] = "/broken/thing"
        self._index.unindex_object(1)

    def testRoot(self):

        self._populateIndex()
        tests = ( ("/",0, range(1,19)), )

        for comp,level,results in tests:
            for path in [comp,"/"+comp,"/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path":{'query':path,"level":level}})
                lst = list(res[0].keys())
                self.assertEqual(lst,results)

        for comp,level,results in tests:
            for path in [comp,"/"+comp,"/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path":{'query':( (path,level),)}})
                lst = list(res[0].keys())
                self.assertEqual(lst,results)

    def testRoot(self):

        self._populateIndex()
        tests = ( ("/",0, range(1,19)), )

        for comp,level,results in tests:
            for path in [comp,"/"+comp,"/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path":{'query':path,"level":level}})
                lst = list(res[0].keys())
                self.assertEqual(lst,results)

        for comp,level,results in tests:
            for path in [comp,"/"+comp,"/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path":{'query':( (path,level),)}})
                lst = list(res[0].keys())
                self.assertEqual(lst,results)


    def testSimpleTests(self):

        self._populateIndex()
        tests = [
            ("aa", 0, [1,2,3,4,5,6,7,8,9]),
            ("aa", 1, [1,2,3,10,11,12] ),
            ("bb", 0, [10,11,12,13,14,15,16,17,18]),
            ("bb", 1, [4,5,6,13,14,15] ),
            ("bb/cc", 0, [16,17,18] ),
            ("bb/cc", 1, [6,15] ),
            ("bb/aa", 0, [10,11,12] ),
            ("bb/aa", 1, [4,13] ),
            ("aa/cc", -1, [3,7,8,9,12] ),
            ("bb/bb", -1, [5,13,14,15] ),
            ("18.html", 3, [18] ),
            ("18.html", -1, [18] ),
            ("cc/18.html", -1, [18] ),
            ("cc/18.html", 2, [18] ),
        ]

        for comp,level,results in tests:
            for path in [comp,"/"+comp,"/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path":{'query':path,"level":level}})
                lst = list(res[0].keys())
                self.assertEqual(lst,results)

        for comp,level,results in tests:
            for path in [comp,"/"+comp,"/"+comp+"/"]:
                res = self._index._apply_index(
                                    {"path":{'query':( (path,level),)}})
                lst = list(res[0].keys())
                self.assertEqual(lst,results)

    def testComplexOrTests(self):

        self._populateIndex()
        tests = [
            (['aa','bb'],1,[1,2,3,4,5,6,10,11,12,13,14,15]),
            (['aa','bb','xx'],1,[1,2,3,4,5,6,10,11,12,13,14,15]),
            ([('cc',1),('cc',2)],0,[3,6,7,8,9,12,15,16,17,18]),
        ]

        for lst ,level,results in tests:

            res = self._index._apply_index(
                            {"path":{'query':lst,"level":level,"operator":"or"}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)

    def testComplexANDTests(self):

        self._populateIndex()
        tests = [
            (['aa','bb'],1,[]),
            ([('aa',0),('bb',1)],0,[4,5,6]),
            ([('aa',0),('cc',2)],0,[3,6,9]),
        ]

        for lst ,level,results in tests:
            res = self._index._apply_index(
                            {"path":{'query':lst,"level":level,"operator":"and"}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)

class TestExtendedPathIndex( ExtendedPathIndexTestCase ):
    """ Test ExtendedPathIndex objects """

    def testIndexIntegrity(self):
        self._populateIndex()
        index = self._index._index
        self.assertEqual(list(index[None][0].keys()), [1,8,16])
        self.assertEqual(list(index[None][1].keys()), [2,9,10,17,18])
        self.assertEqual(list(index[None][2].keys()), [3,5,11,13])
        self.assertEqual(list(index[None][3].keys()), [4,6,7,12,14,15])

    def testUnIndexError(self):
        self._populateIndex()
        # this should not raise an error
        self._index.unindex_object(-1)

        # nor should this
        self._index._unindex[1] = "/broken/thing"
        self._index.unindex_object(1)

    def testDepthLimit(self):
        self._populateIndex()
        tests = [
            ('/',0,1,0,[1,8,16]),
            ('/',0,2,0,[1,2,8,9,10,16,17,18]),
            ('/',0,3,0,[1,2,3,5,8,9,10,11,13,16,17,18]),
            ]
        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path":{'query':lst,"level":level,"operator":"and", "depth":depth,"navtree":navtree}})
            lst = list(res[0].keys())
#            if not lst == results:
#                import pdb;pdb.set_trace()
            self.assertEqual(lst,results)

    def testNavtree(self):
        self._populateIndex()
        tests = [
            ('/'        ,0,0,1,[1,8,16]),
            ('/aa'      ,0,0,1,[1,2,8,9,16]),
            ('/aa'      ,1,0,1,[2,3,9,10,13,17,18]),
            ('/aa/aa'   ,0,0,1,[1,2,3,8,9,16]),
            ('/aa/aa/aa',0,0,1,[1,2,3,4,8,9,16]),
            ('/aa/bb'   ,0,0,1,[1,2,5,8,9,16]),
            ('/bb'      ,0,0,1,[1,8,10,16,17,18]),
            ('/bb/aa'   ,0,0,1,[1,8,10,13,16,17,18]),
            ('/bb/bb'   ,0,0,1,[1,8,10,11,16,17,18]),
            ]
        for lst, level, depth, navtree, results in tests:
            res = self._index._apply_index(
                {"path":{'query':lst,"level":level,"operator":"and", "depth":depth,"navtree":navtree}})
            lst = list(res[0].keys())
            self.assertEqual(lst,results)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPathIndex))
    suite.addTest(makeSuite(TestExtendedPathIndex))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    main()
