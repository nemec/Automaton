import sys
import Pyro.core
from automaton.lib.exceptions import *
from automaton.client.base import ClientInterface

class ClientWrapper(ClientInterface):

  def __init__(self, server='localhost', port=9090, appname="AutomatonClient"):
    self.appname = appname
    self.clientid = None
    self.client = Pyro.core.getProxyForURI(
                    "PYROLOC://{0}:{1}/automaton".format(server, port))

  def open(self):
    """Open a connection to the server and register the client."""
    self.clientid = self.client.registerClient(self.appname)

  def close(self):
    "Unregister from the server then close the connection."
    self.client.unregisterClient(self.clientid)
