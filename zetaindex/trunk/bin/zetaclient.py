#!/usr/bin/env python

from zetaserver.Client import Client
from zetaserver.protocols import Index

Index.Client._listen = True
client = Client(Index.Client)
client.scheme = 'foo'
client._listen = True
import code; code.interact(local=locals())
