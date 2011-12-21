"""These are the exceptions that may be raised by the server."""


class ServiceNotProvidedError(Exception):
  """Raised if the client tries to request a service that doesn't exist."""
  def __init__(self, action=None):
    super(ServiceNotProvidedError, self).__init__()
    self.action = action

  def __str__(self):
    if self.action:
      return "Command {0} is unknown.".format(repr(self.action))
    else:
      return "Command is not unknown."


class ServiceNotRegisteredError(Exception):
  """Raised if the client tries to request a service that exists, but
  hasn't been explicitly registered for the current client. Prevents
  rogue users from executing arbitrary commands.

  """
  def __init__(self, action=None):
    super(ServiceNotRegisteredError, self).__init__()
    self.action = action

  def __str__(self):
    if self.action:
      return "Command {0} is not registered.".format(repr(self.action))
    else:
      return "Command is not registered."


class ClientNotRegisteredError(Exception):
  """Raised if the client passes along a ClientID that is not registered
  with the server. The ClientID is used to associate a client with only
  the commands it has explicitly registered.

  """
  pass


class UnknownIntentError(Exception):
  """Exception raised when the server receives a query that it does not know
  how to interpret.

  """
  pass


class ClientError(Exception):
  """Exception that represents errors in the client, regardless of
  implementation.

  """
  pass
