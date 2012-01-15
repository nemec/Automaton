from __future__ import absolute_import
import sys
import time

# pylint: disable-msg=E0611
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
# pylint: enable-msg=E0611

from automaton.lib.thrift.python import AutomatonThrift
from automaton.lib.thrift.python.ttypes import *

from automaton.client.base import ClientInterface
import automaton.lib.logger as logger
import automaton.lib.exceptions

automaton.lib.exceptions.ClientError = Thrift.TException


class ClientWrapper(ClientInterface):

  def __init__(self, server='localhost', port=9090, appname="AutomatonClient"):
    ClientInterface.__init__(self, server, port)
    self.appname = appname
    self.transport = TSocket.TSocket(server, port)
    self.transport = TTransport.TBufferedTransport(self.transport)
    protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
    self.client = AutomatonThrift.Client(protocol)
    self.clientid = None

  # Opens a connection to the server and registers the client
  def open(self):
    for x in xrange(5, 10, 25):
      try:
        self.transport.open()
        self.clientid = self.client.registerClient(self.appname)
        return
      except automaton.lib.exceptions.ClientError:
        logger.log("Failed to connect to Thrift server. "
                    "Retrying in {0} seconds.".format(x))
        time.sleep(x)
    raise ClientException("Failed to connect to Thrift server. Exiting.")

  # Unregisters from the server then closes the connection
  def close(self):
    self.client.unregisterClient(self.clientid)
    self.transport.close()
