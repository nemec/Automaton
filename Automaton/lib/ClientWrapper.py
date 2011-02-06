import sys

from ClientInterface import ClientInterface
import time
import Automaton.lib.logger as logger

from automaton_thrift.python import Script
from automaton_thrift.python.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

WrapperException=Thrift.TException

class ClientWrapper(ClientInterface):

  def __init__(self, server='localhost', port=9090):
    self.transport = TSocket.TSocket(server, port)
    self.transport = TTransport.TBufferedTransport(self.transport)
    protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
    self.client = Script.Client(protocol)
  
  # Opens a connection to the server and registers the client
  def open(self):
    for x in xrange(5, 26, 10):
      try:
        self.transport.open()
        self.serviceid = self.client.registerService()
        return
      except WrapperException:
        logger.log("Failed to connect to Thrift server. Retrying in %d seconds." % (x))
        time.sleep(x)
    raise WrapperException("Failed to connect to Thrift server. Exiting.")

  # Unregisters from the server then closes the connection
  def close(self):
    self.client.unregisterService(self.serviceid)
    self.transport.close()

