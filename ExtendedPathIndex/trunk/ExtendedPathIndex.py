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

from types import StringType, ListType, TupleType

from Globals import Persistent, DTMLFile
from OFS.SimpleItem import SimpleItem
from BTrees.IOBTree import IOBTree
from BTrees.OOBTree import OOBTree
from BTrees.IIBTree import IITreeSet, IISet, intersection, union
from BTrees.Length import Length
from zLOG import LOG, ERROR

from Products.PluginIndexes import PluggableIndex
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.PluginIndexes.common import safe_callable
from Products.PluginIndexes.PathIndex.PathIndex import PathIndex

_marker = []

class ExtendedPathIndex(PathIndex):
    """ A path index stores all path components of the physical
    path of an object:

    Internal datastructure (regular pathindex):

    - a physical path of an object is split into its components

    - every component is kept as a  key of a OOBTree in self._indexes

    - the value is a mapping 'level of the path component' to
      'all docids with this path component on this level'

    In addition
    
    - there is a terminator (None) signifying the last component in the path

    """

    meta_type="ExtendedPathIndex"

    manage_options= (
        {'label': 'Settings',
         'action': 'manage_main',
         'help': ('ExtendedPathIndex','ExtendedPathIndex_Settings.stx')},
    )

    query_options = ("query", "level", "operator", "depth", "navtree")

    def index_object(self, docid, obj ,threshold=100):
        """ hook for (Z)Catalog """

        f = getattr(obj, self.id, None)
        if f is not None:
            if safe_callable(f):
                try:
                    path = f()
                except AttributeError:
                    return 0
            else:
                path = f

            if not isinstance(path, (StringType, TupleType)):
                raise TypeError('path value must be string or tuple of strings')
        else:
            try:
                path = obj.getPhysicalPath()
            except AttributeError:
                return 0

        if isinstance(path, (ListType, TupleType)):
            path = '/'+ '/'.join(path[1:])
        comps = filter(None, path.split('/'))
       
        if not self._unindex.has_key(docid):
            self._migrate_length()
            self._length.change(1)

        for i in range(len(comps)):
            self.insertEntry(comps[i], docid, i)

        # Add terminator
        self.insertEntry(None, docid, len(comps)-1)

        self._unindex[docid] = path
        return 1

    def unindex_object(self, docid):
        """ hook for (Z)Catalog """

        if not self._unindex.has_key(docid):
            LOG(self.__class__.__name__, ERROR,
                'Attempt to unindex nonexistent document'
                ' with id %s' % docid)
            return

        comps =  self._unindex[docid].split('/')

        def unindex(comp, level, docid=docid):
            try:
                self._index[comp][level].remove(docid)

                if not self._index[comp][level]:
                    del self._index[comp][level]

                if not self._index[comp]:
                    del self._index[comp]
            except KeyError:
                LOG(self.__class__.__name__, ERROR,
                    'Attempt to unindex document'
                    ' with id %s failed' % docid)

        for level in range(len(comps[1:])):
            comp = comps[level+1]
            unindex(comp, level)


        # Remove the terminator
        level = len(comps[1:])
        comp = None
        unindex(comp, level-1)

        self._migrate_length()
        self._length.change(-1)
        del self._unindex[docid]

    def search(self, path, default_level=0, depth=0, navtree=0):
        """
        path is either a string representing a
        relative URL or a part of a relative URL or
        a tuple (path,level).

        level >= 0  starts searching at the given level
        level <  0  not implemented yet
        """

        if isinstance(path, StringType):
            startlevel = default_level
        else:
            startlevel = int(path[1])
            path  = path[0]

        comps = filter(None, path.split('/'))

        if len(comps) == 0:
            if not depth and not navtree:
                return IISet(self._unindex.keys())

        # Make sure that we get depth = 1 if in navtree mode
        depth = depth or navtree

        if startlevel >= 0:

            pathset = None
            navset  = None
            depthset = None

            if navtree and \
                   self._index.has_key(None) and \
                   self._index[None].has_key(startlevel):
                navset = self._index[None][startlevel]

            for level in range(startlevel, startlevel+len(comps) + depth):
                if level-startlevel < len(comps):
                    comp = comps[level-startlevel]
                    if not self._index.has_key(comp): return IISet()
                    if not self._index[comp].has_key(level): return IISet()
                    pathset = intersection(pathset, self._index[comp][level])
                    if navtree and \
                           self._index.has_key(None) and \
                           self._index[None].has_key(level+1):
                        navset  = union(navset, intersection(pathset, self._index[None][level+1]))
                if level-startlevel >= len(comps) or navtree:
                    if self._index.has_key(None) and self._index[None].has_key(level):
                        depthset = union(depthset, intersection(pathset, self._index[None][level]))

            if navtree:
                return union(depthset, navset) or IISet()
            else:
                return intersection(pathset,depthset) or IISet()

        else:
            results = IISet()
            for level in range(0,self._depth + 1):
                ids = None
                error = 0
                for cn in range(0,len(comps)):
                    comp = comps[cn]
                    try:
                        ids = intersection(ids,self._index[comp][level+cn])
                    except KeyError:
                        error = 1
                if error==0:
                    results = union(results,ids)
            return results

    def _apply_index(self, request, cid=''):
        """ hook for (Z)Catalog
            'request' --  mapping type (usually {"path": "..." }
             additionaly a parameter "path_level" might be passed
             to specify the level (see search())

            'cid' -- ???
        """

        record = parseIndexRequest(request,self.id,self.query_options)
        if record.keys==None: return None

        level    = record.get("level",0)
        operator = record.get('operator',self.useOperator).lower()
        depth    = record.get('depth',0)
        navtree  = record.get('navtree',0)

        # depending on the operator we use intersection of union
        if operator == "or":  set_func = union
        else: set_func = intersection

        res = None
        for k in record.keys:
            rows = self.search(k,level, depth, navtree)
            res = set_func(res,rows)

        if res:
            return res, (self.id,)
        else:
            return IISet(), (self.id,)

    index_html = DTMLFile('dtml/index', globals())
    manage_workspace = DTMLFile('dtml/manageExtendedPathIndex', globals())


manage_addExtendedPathIndexForm = DTMLFile('dtml/addExtendedPathIndex', globals())

def manage_addExtendedPathIndex(self, id, REQUEST=None, RESPONSE=None, URL3=None):
    """Add an extended path index"""
    return self.manage_addIndex(id, 'ExtendedPathIndex', extra=None, \
                REQUEST=REQUEST, RESPONSE=RESPONSE, URL1=URL3)
