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


def initialize(context):
    from Products.ExtendedPathIndex.ExtendedPathIndex import ExtendedPathIndex
    from Products.ExtendedPathIndex.ExtendedPathIndex import manage_addExtendedPathIndex, manage_addExtendedPathIndexForm

    context.registerClass(
        ExtendedPathIndex,
        permission='Add Pluggable Index',
        constructors=(manage_addExtendedPathIndexForm,
                      manage_addExtendedPathIndex),
        icon='www/index.gif',
        visibility=None
    )
