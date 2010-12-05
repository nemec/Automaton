#!/usr/bin/env python

import sys
# Keeping these here until I get the installer script working =/
sys.path.append('/home/dan/prg/py/Automaton/Automaton')
sys.path.append('/home/dan/prg/py/Automaton/gen-py')
from automaton_thrift import Script
import automaton_thrift.ttypes

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import Automaton.lib.AutomatonServer as AutomatonServer

class ThriftServer(AutomatonServer.AutomatonServer):
  def __init__(self, port = 9090):
    AutomatonServer.AutomatonServer.__init__(self)
    self.port = port
    self.Exceptions = automaton_thrift.ttypes

  def initialize(self):
    processor = Script.Processor(self)
    transport = TSocket.TServerSocket(self.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    #Threaded server allows for multiple connections
    self.server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

  def start(self):
    self.server.serve()

if __name__=="__main__":
  server = ThriftServer()

  server.initialize()

  print 'Starting the server...'
  try:
    server.start()
  except KeyboardInterrupt:
    pass

