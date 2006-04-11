#!/usr/local/bin/python
"""httpy -- a straightforward Python webserver. `man 1 httpy' for details.
"""
from httpy.utils import couple
from httpy.responders.multiple import Responder as Multiple

couple(Multiple())
