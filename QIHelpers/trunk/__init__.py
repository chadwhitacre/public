from AccessControl import ModuleSecurityInfo
from Products.CMFCore.DirectoryView import registerDirectory
from config import *
from pprint import pformat
from utils import *

import Skinstall
import FolderTypes
import CatalogInstall

security = ModuleSecurityInfo()
security.declarePublic('pformat')
security.declarePublic('mxNow','mxToday','mxDateTime','mxRelativeDateTime', 'mx_to_zope','zope_to_mx')
security.declarePublic('lists_to_csv','csv_to_lists')
security.declarePublic('request_dict')
security.apply(globals())


registerDirectory(SKINS_DIR, GLOBALS)
