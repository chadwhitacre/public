#!/usr/local/bin/python
"""httpy -- a straightforward Python webserver. `man 1 httpy' for details.
"""
from httpy import couple
from httpy.responders import Multiple

couple(Multiple())
