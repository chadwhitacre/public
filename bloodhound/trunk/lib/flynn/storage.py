import os
import sys
from threading import Lock

import rdflib


# The db is located in the magic directory. If you want it elsewhere, link it.
db_path = os.path.join(sys.path[0], '../db')
db = rdflib.Graph('Sleepycat')
db.open(db_path)

acn_users = "http://www.zetadev.com/xmlns/acn/users/"
db.bind("acn-users", acn_users, True)
USERS = rdflib.Namespace(acn_users)

acn_usermgmt = "http://www.zetadev.com/xmlns/acn/usermgmt/"
db.bind("acn-usermgmt", acn_usermgmt, True)
USERMGMT = rdflib.Namespace(acn_usermgmt)

write_lock = Lock()
