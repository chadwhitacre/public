""" alter sys.path for testing purposes """
import os, sys

cwd = os.getcwd() # this should be tests/ 
sep = os.sep
#porter_location = sep.join(cwd.split(sep)[:-2]) # this should be site-packages/
#sys.path.insert(1,porter_location) 
# afaict sys.path[0] == os.getcwd(). We use sys.path[0] as the base for our data directory
# so if this was ever set to site-packages/porter while testing we would be acting on live
# data!

