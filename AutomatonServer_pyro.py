#!/usr/bin/env python

import sys
# Keeping these here until I get the installer script working =/
sys.path.append('/home/dan/prg/py/Automaton/Automaton')
sys.path.append('/home/dan/prg/py/Automaton/gen-py')

import Pyro.core

import Automaton.lib.AutomatonServer as AutomatonServer

class PyroServer(Pyro.core.ObjBase, AutomatonServer.AutomatonServer):
  #pass
  def __init__(self):
    Pyro.core.ObjBase.__init__(self)
    AutomatonServer.AutomatonServer.__init__(self)

if __name__=="__main__":
  Pyro.core.initServer()
  daemon=Pyro.core.Daemon(port=9090)
  uri = daemon.connect(PyroServer(), "automaton")

  print 'Starting the server...'
  try:
    daemon.requestLoop()
  except KeyboardInterrupt:
    pass

