#!/usr/bin/env python

import sys

import Pyro.core

import Automaton.lib.AutomatonServer as AutomatonServer

class PyroServer(Pyro.core.ObjBase, AutomatonServer.AutomatonServer):

  daemon = None

  def __init__(self, withgui = False):
    AutomatonServer.AutomatonServer.__init__(self, withgui)
    Pyro.core.ObjBase.__init__(self)

  def initialize(self):
    Pyro.core.initServer()
    PyroServer.daemon=Pyro.core.Daemon(port=9090)
    PyroServer.daemon.connect(self, "automaton")
    self.initialized = True

  def _start(self):
    if self.initialized:
      PyroServer.daemon.requestLoop()
    else:
      print "Error. Server not initialized"

if __name__=="__main__":
  server = PyroServer()

  server.initialize()

  print 'Starting the server...'
  try:
    server.start()
  except KeyboardInterrupt:
    pass

