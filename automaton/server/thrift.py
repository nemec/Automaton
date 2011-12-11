#!/usr/bin/env python

from __future__ import absolute_import

import sys
from automaton.lib.thrift.python import AutomatonThrift
import automaton.lib.thrift.python.ttypes

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from automaton.server.base import AutomatonServer


class ThriftServer(AutomatonServer):
  def __init__(self, withgui=False, port=9090):
    AutomatonServer.__init__(self, withgui)
    self.port = port
    self.exceptions = automaton.lib.thrift.python.ttypes

  def initialize(self):
    processor = AutomatonThrift.Processor(self)
    transport = TSocket.TServerSocket(port=self.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    #Threaded server allows for multiple connections
    self.server = TServer.TThreadedServer(processor,
                                        transport, tfactory, pfactory)

  def _start(self):
    self.server.serve()


if __name__ == "__main__":
  server = ThriftServer()

  server.initialize()

  print 'Starting the server...'
  try:
    server.start()
  except KeyboardInterrupt:
    pass
