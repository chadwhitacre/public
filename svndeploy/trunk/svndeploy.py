#!/usr/bin/env python
# (c) 2005 Chad Whitacre <http://www.zetaweb.com/>
# This program is beerware. If you like it, buy me a beer someday.
# No warranty is expressed or implied.

import os
from popen2 import Popen4

path = os.path.realpath('.')

command = 'svn info'



def _popen(command)
    process = Popen4(command)
    result = process.wait()
    output = process.fromchild.read()
    return (result, output)


if __name__ == '__main__':
    print path