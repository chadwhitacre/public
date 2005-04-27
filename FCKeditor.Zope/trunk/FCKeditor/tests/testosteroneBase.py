#!/usr/bin/env python
import os, sys, time
from pprint import pprint
from testosterone import testosterone, catchException

# make sure we can find ourselves
sys.path.insert(1, os.path.realpath('..'))

# the thing we want to test
from FCKeditor import FCKeditor, FCKexception
from data import testdata


##
# run some tests!
##

testosterone("""\

fck = FCKeditor()

# set some config and test the querystring getter
exec fck.SetConfig('AutoDetectLanguage','false')
exec fck.SetConfig('DefaultLanguage','pt-BR')
qs = fck.GetConfigQuerystring()
qs == "AutoDetectLanguage=false&DefaultLanguage=pt-BR"


# now make sure url encoding works
fck = FCKeditor()
exec fck.SetConfig('foo','&I need:  "URL encoding"')
exec fck.SetConfig('so do *I*','bar')
qs = fck.GetConfigQuerystring()
qs == "foo=%26I+need%3A++%22URL+encoding%22&so+do+%2AI%2A=bar"


# and now check the replacement itself
fck = FCKeditor()
fck.SetCompatible(testdata.COMPATIBLE_USERAGENT)
fck.Create() == testdata.FCKEDITOR_STOCK


# try out a custom replacement
fck = FCKeditor()
exec fck.SetConfig('AutoDetectLanguage','false')
exec fck.SetConfig('DefaultLanguage','pt-BR')
fck.InstanceName = 'CustomEditor'
fck.Width = 300  # int should be converted to '300px'
fck.Height = 400
fck.ToolbarSet = 'CustomToolbar'
fck.BasePath = '/AltPath/'
fck.Value = testdata.VALUE

exec fck.SetCompatible(testdata.COMPATIBLE_USERAGENT)
fck.Create() == testdata.FCKEDITOR_CUSTOM

# test the validation of Compatible in Create
fck = FCKeditor()
exc = catchException(fck.Create)
exc is FCKexception


# test our useragent validation
False not in [fck.SetCompatible(ua) for ua in testdata.COMPATIBLE_USERAGENTS]
True not in [fck.SetCompatible(ua) for ua in testdata.INCOMPATIBLE_USERAGENTS]

""", globals(), locals())