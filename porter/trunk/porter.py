#!/usr/local/bin/python
from PorterCmd import PorterCmd
import sys

def main():
    c = PorterCmd('/usr/local/apache2/conf/vhosts')
    try:
        c.cmdloop()
    except KeyboardInterrupt:
        c.onecmd("EOF")

if __name__ == '__main__':
    main()
