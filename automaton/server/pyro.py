#!/usr/bin/env python

import Pyro.core

from automaton.server.base import AutomatonServer


class PyroServer(Pyro.core.ObjBase, AutomatonServer):
  """Implementation of the Automaton Server with PYRO."""
  daemon = None

  def __init__(self, withgui=False, port=9090):
    AutomatonServer.__init__(self, withgui)
    Pyro.core.ObjBase.__init__(self)
    self.port = port
    self.initialized = False

  def initialize(self):
    """Initialize the Pyro server."""
    Pyro.core.initServer()
    PyroServer.daemon = Pyro.core.Daemon(port=self.port)
    PyroServer.daemon.connect(self, "automaton")
    self.initialized = True

  def _start(self):
    """Start the server."""
    if self.initialized:
      PyroServer.daemon.requestLoop()
    else:
      print "Error. Server not initialized"


if __name__ == "__main__":
  # pylint: disable-msg=C0103
  server = PyroServer()

  server.initialize()

  print 'Starting the server...'
  try:
    server.start()
  except KeyboardInterrupt:
    pass
