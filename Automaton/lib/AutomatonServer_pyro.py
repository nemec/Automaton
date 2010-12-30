#!/usr/bin/env python

import sys

import Pyro.core

import Automaton.lib.AutomatonServer as AutomatonServer

class PyroServer(Pyro.core.ObjBase, AutomatonServer.AutomatonServer):
  #pass
  def __init__(self):
    AutomatonServer.AutomatonServer.__init__(self)
    Pyro.core.ObjBase.__init__(self)

  def initialize(self):
    Pyro.core.initServer()
    self.daemon=Pyro.core.Daemon(port=9090)
    self.daemon.connect(PyroServer(), "automaton")
    self.initialized = True

  def start(self):
    if self.initialized:
      self.daemon.requestLoop()
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

