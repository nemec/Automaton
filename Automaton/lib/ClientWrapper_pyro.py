import sys
import Pyro.core

class ClientWrapper:

  def __init__(self, server='localhost', port=9090):
    self.client = Pyro.core.getProxyForURI("PYROLOC://%s:%s/automaton" % (server, port))
  
  # Opens a connection to the server and registers the client
  def open(self):
    self.serviceid = self.client.registerService()

  # Unregisters from the server then closes the connection
  def close(self):
    self.client.unregisterService(self.serviceid)

  def getAvailableScripts(self):
    return self.client.getAvailableScripts()

  def isScript(self, scriptname):
    return self.client.isScript(scriptname)

  def registerScript(self, scriptname):
    return self.client.registerScript(self.serviceid, scriptname)

  def unregisterScript(self, scriptname):
    return self.client.registerScript(self.serviceid, scriptname)

  def execute(self, scriptname, args):
    return self.client.execute(self.serviceid, scriptname, args)

  def scriptUsage(self, scriptname):
    return self.client.scriptUsage(scriptname)
