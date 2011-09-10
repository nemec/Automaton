# These are the exceptions that may be raised by the server


# Raised if the client tries to request a service that doesn't exist.
class ServiceNotProvidedError(Exception):
  def __init__(self, action=None):
    self.action = action

  def __str__(self):
    if self.action:
      return "Command {0} is unknown.".format(repr(self.action))
    else:
      return "Command is not unknown."


# Raised if the client tries to request a service that exists, but
# hasn't been explicitly registered for the current client. Prevents
# rogue users from executing arbitrary commands.
class ServiceNotRegisteredError(Exception):
  def __init__(self, action=None):
    self.action = action

  def __str__(self):
    if self.action:
      return "Command {0} is not registered.".format(repr(self.action))
    else:
      return "Command is not registered."


# Raised if the client passes along a ClientID that is not registered
# with the server. The ClientID is used to associate a client with only
# the commands it has explicitly registered.
class ClientNotRegisteredError(Exception):
  pass


class ModuleLoadError(Exception):
  pass
