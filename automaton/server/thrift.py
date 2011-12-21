#!/usr/bin/env python

from __future__ import absolute_import

from automaton.lib.thrift.python import AutomatonThrift
import automaton.lib.thrift.python.ttypes

# pylint: disable-msg=E0611
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
# pylint: enable-msg=E0611

import automaton.lib.exceptions
from automaton.server.base import AutomatonServer

automaton.lib.exceptions = automaton.lib.thrift.python.ttypes


class ThriftServer(AutomatonServer):
  """Implements Automaton's server over the Thrift interface."""
  def __init__(self, withgui=False, port=9090):
    AutomatonServer.__init__(self, withgui)
    self.port = port
    self.server = None

  def initialize(self):
    """Initialize the Thrift connection."""
    processor = AutomatonThrift.Processor(self)
    transport = TSocket.TServerSocket(port=self.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    #Threaded server allows for multiple connections
    self.server = TServer.TThreadedServer(processor,
                                        transport, tfactory, pfactory)

  def _start(self):
    """Start the server."""
    self.server.serve()


if __name__ == "__main__":
  # pylint: disable-msg=C0103
  server = ThriftServer()

  server.initialize()

  print 'Starting the server...'
  try:
    server.start()
  except KeyboardInterrupt:
    pass
