import sys
sys.path.append('/home/dan/prg/py/Automaton/gen-py')

from ClientInterface import ClientInterface

from automaton_thrift import Script
from automaton_thrift.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

ThriftException=Thrift.TException

class ClientWrapper(ClientInterface):

  def __init__(self, server='localhost', port=9090):
    self.transport = TSocket.TSocket(server, port)
    self.transport = TTransport.TBufferedTransport(self.transport)
    protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
    self.client = Script.Client(protocol)
  
  # Opens a connection to the server and registers the client
  def open(self):
    self.transport.open()
    self.serviceid = self.client.registerService()

  # Unregisters from the server then closes the connection
  def close(self):
    self.client.unregisterService(self.serviceid)
    self.transport.close()

