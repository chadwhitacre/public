#!/usr/local/bin/python
from PorterCmd import PorterCmd
import sys

def main():
    c = PorterCmd('/usr/local/apache2/conf/vhosts')
    c.cmdloop()

if __name__ == '__main__':
    main()
