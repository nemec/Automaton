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

  def interpret(self, raw):
    return self.client.interpret(self.serviceid, raw)

  def scriptUsage(self, scriptname):
    return self.client.scriptUsage(scriptname)
