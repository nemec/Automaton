import sys

from ClientInterface import ClientInterface
import time
import Automaton.lib.logger as logger

from automaton_thrift.python import AutomatonThrift
from automaton_thrift.python.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

ClientException=Thrift.TException

class ClientWrapper(ClientInterface):

  def __init__(self, server='localhost', port=9090, appname="AutomatonClient"):
    self.appname = appname
    self.transport = TSocket.TSocket(server, port)
    self.transport = TTransport.TBufferedTransport(self.transport)
    protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
    self.client = AutomatonThrift.Client(protocol)
    self.clientid = None
  
  # Opens a connection to the server and registers the client
  def open(self):
    for x in xrange(5, 26, 10):
      try:
        self.transport.open()
        self.clientid = self.client.registerClient(self.appname)
        return
      except ClientException:
        logger.log("Failed to connect to Thrift server. Retrying in {0} seconds.".format(x))
        time.sleep(x)
    raise ClientException("Failed to connect to Thrift server. Exiting.")

  # Unregisters from the server then closes the connection
  def close(self):
    self.client.unregisterClient(self.clientid)
    self.transport.close()

