#!/usr/bin/env python

import sys
from automaton_thrift.python import AutomatonThrift
import automaton_thrift.python.ttypes

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import Automaton.lib.AutomatonServer as AutomatonServer

class ThriftServer(AutomatonServer.AutomatonServer):
  def __init__(self, withgui = False, port = 9090):
    AutomatonServer.AutomatonServer.__init__(self, withgui)
    self.port = port
    self.exceptions = automaton_thrift.python.ttypes

  def initialize(self):
    processor = AutomatonThrift.Processor(self)
    transport = TSocket.TServerSocket(self.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    #Threaded server allows for multiple connections
    self.server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

  def _start(self):
    self.server.serve()

if __name__=="__main__":
  server = ThriftServer()

  server.initialize()

  print 'Starting the server...'
  try:
    server.start()
  except KeyboardInterrupt:
    pass

