#!/usr/local/bin/python
from Porter import Porter, PorterError
from ConfigParser import RawConfigParser

cp = RawConfigParser()
conf_filenames = cp.read('porter.conf')
db_path = cp.get('default','db_path')

def main():
    c = Porter(db_path)
    try:
        c.cmdloop()
    except KeyboardInterrupt:
        c.onecmd("EOF")

if __name__ == '__main__':
    main()
