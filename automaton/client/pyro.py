import sys
import Pyro.core
from exceptions import *
from automaton.client.base import ClientInterface

class ClientException(Exception):
  pass

class ClientWrapper(ClientInterface):

  def __init__(self, server='localhost', port=9090, appname="AutomatonClient"):
    self.appname = appname
    self.clientid = None
    self.client = Pyro.core.getProxyForURI("PYROLOC://{0}:{1}/automaton".format(server, port))
  
  # Opens a connection to the server and registers the client
  def open(self):
    self.clientid = self.client.registerClient(self.appname)

  # Unregisters from the server then closes the connection
  def close(self):
    self.client.unregisterClient(self.clientid)

