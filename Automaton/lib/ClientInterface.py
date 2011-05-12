import sys

class ClientInterface:
  
  def __init__(self, server='localhost', port=9090):
    self.client = None

  # Opens a connection to the server and registers the client
  def open(self):
    self.serviceid = None

  # Unregisters from the server then closes the connection
  def close(self):
    pass

  def getAvailablePlugins(self):
    return self.client.getAvailablePlugins()

  def isPlugin(self, name):
    return self.client.isPlugin(name)

  def registerPlugin(self, name):
    return self.client.registerPlugin(self.serviceid, name)

  def unregisterPlugin(self, name):
    return self.client.registerPlugin(self.serviceid, name)

  def execute(self, name, args):
    return self.client.execute(self.serviceid, name, args)

  def interpret(self, raw):
    return self.client.interpret(self.serviceid, raw)

  def pluginUsage(self, name):
    return self.client.pluginUsage(name)
