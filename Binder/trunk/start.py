import sys
from os.path import join
from Binder import Binder
from ConfigParser import RawConfigParser

def main():
    c = Binder()
    try:
        c.cmdloop()
    except KeyboardInterrupt:
        c.onecmd("EOF")

if __name__ == '__main__':
    main()
