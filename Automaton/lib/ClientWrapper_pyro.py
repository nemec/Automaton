import sys
import Pyro.core
from exceptions import *
from ClientInterface import ClientInterface

class ClientException(Exception):
  pass

class ClientWrapper(ClientInterface):

  def __init__(self, server='localhost', port=9090, appname="AutomatonClient"):
    self.appname = appname
    self.client = Pyro.core.getProxyForURI("PYROLOC://%s:%s/automaton" % (server, port))
  
  # Opens a connection to the server and registers the client
  def open(self):
    self.serviceid = self.client.registerService(self.appname)

  # Unregisters from the server then closes the connection
  def close(self):
    self.client.unregisterService(self.serviceid)

