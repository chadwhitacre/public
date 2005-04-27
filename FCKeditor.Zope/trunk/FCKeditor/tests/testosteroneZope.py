"""Zope-specific tests; requires ZopeTestCase
"""

from testosterone import testosterone, catchException

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
ZopeTestCase.installProduct('FCKeditor')

from zExceptions import BadRequest
from Products.FCKeditor.ZopeFCKeditor import ZopeFCKeditor
from data import testdata

app = ZopeTestCase.app()




##
# start testing!
##

testosterone("""\

add = app.manage_addProduct['FCKeditor'].manage_addFCKeditor

exec add('fck')
hasattr(app, 'fck')
isinstance(app.fck, ZopeFCKeditor)

# test the InstanceName scrubber
app.fck.InstanceName == 'fck'

# Zope does do some ID validation -- [^a-zA-Z0-9-_~,.$\(\)# ]
exc = catchException(add, "123-456fck2_oh yeah, believe-it!!!!BABY!!!!!!!~@#$%$#!)'(*@PO#JTKHEE.")
exc is BadRequest

# But CSS identifier rules are even stricter -- [^a-zA-Z0-9-]
SAFE_FOR_ZOPE = "123-456fck2_oh yeah, believe-itBABY~#$$#)(PO#JTKHEE."
SAFE_FOR_CSS  = "fck2-oh-yeah--believe-itBABY-------PO-JTKHEE-"
exec add(SAFE_FOR_ZOPE)
hasattr(app, SAFE_FOR_ZOPE)
getattr(app, SAFE_FOR_ZOPE).InstanceName == SAFE_FOR_CSS


reset

# test FCKmanager

add = app.manage_addProduct['FCKeditor'].manage_addFCKmanager
exec add('fckmanager')

# afaict we in fact can't constrain programmatic addition of objects
exec app.fckmanager.manage_addProduct['OFSP'].manage_addFolder('foo')
hasattr(app.fckmanager, 'foo')

# instantiate a textarea
fckeditor = app.fckmanager.spawn('MyField')
isinstance(fckeditor, ZopeFCKeditor)
exec fckeditor.SetCompatible(testdata.INCOMPATIBLE_USERAGENT)
fckeditor.Create() == testdata.TEXTAREA

# instantiate an FCKeditor
fckeditor = app.fckmanager.spawn('MyField')
isinstance(fckeditor, ZopeFCKeditor)
exec fckeditor.SetCompatible(testdata.COMPATIBLE_USERAGENT)
fckeditor.Create() == testdata.FCKEDITOR_MYFIELD


""", globals(), locals())

ZopeTestCase.close(app)