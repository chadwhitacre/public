#!/usr/local/bin/python
import sys
from os.path import join
from Porter import Porter, PorterError
from ConfigParser import RawConfigParser

def main():
    c = Porter(var="var")
    try:
        c.cmdloop()
    except KeyboardInterrupt:
        c.onecmd("EOF")

if __name__ == '__main__':
    main()
