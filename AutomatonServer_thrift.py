#!/usr/bin/env python

import sys
# Keeping these here until I get the installer script working =/
sys.path.append('/home/dan/prg/py/Automaton/Automaton')
sys.path.append('/home/dan/prg/py/Automaton/gen-py')
from automaton_thrift import Script
from automaton_thrift.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import Automaton.lib.AutomatonServer as AutomatonServer

if __name__=="__main__":
  handler = AutomatonServer.AutomatonServer()
  processor = Script.Processor(handler)
  transport = TSocket.TServerSocket(9090)
  tfactory = TTransport.TBufferedTransportFactory()
  pfactory = TBinaryProtocol.TBinaryProtocolFactory()

  #Threaded server allows for multiple connections
  server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

  print 'Starting the server...'
  try:
    server.serve()
  except KeyboardInterrupt:
    pass

