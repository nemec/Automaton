# These are the exceptions that may be raised by the server

# Raised if the client tries to execute a command that doesn't exist.
class PluginNotLoadedException(Exception):
  def __init__(self, action = None):
    self.action = action

  def __str__(self):
    if self.action:
      return "Command %s is unknown." % repr(self.action)
    else:
      return "Command is not unknown."

# Raised if the client tries to execute a command that exists, but
# hasn't been explicitly registered for the current service. Prevents
# rogue users from executing arbitrary commands.
class PluginNotRegisteredException(Exception):
  def __init__(self, action = None):
    self.action = action

  def __str__(self):
    if self.action:
      return "Command %s is not registered." % repr(self.action)
    else:
      return "Command is not registered."

# Raised if the client passes along a ServiceID that is not registered
# with the server. The ServiceID is used to associate a client with only
# the commands it has explicitly registered.
class ServiceNotRegisteredException(Exception):
  pass

class ModuleLoadException(Exception):
  pass
