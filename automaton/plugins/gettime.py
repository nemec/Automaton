import time

import automaton.lib.plugin


class GetTime(automaton.lib.plugin.PluginInterface):
  """Plugin that retrieves the system time."""

  def __init__(self, registrar):
    super(GetTime, self).__init__(registrar)

    usage = ("USAGE: %s\n"
             "Returns the current time to the user.")

    registrar.register_service("time", self.execute,
      grammar={}, usage=usage, namespace=__name__)
    registrar.register_service("gettime", self.execute,
      grammar={}, usage=usage, namespace=__name__)

  def disable(self):
    """Disable all of GetTime's services."""
    self.registrar.unregister_service("time", namespace=__name__)
    self.registrar.unregister_service("gettime", namespace=__name__)

  def execute(self, arg='', **kwargs):
    """Return the current system time, in either 12 or 24 hour format."""
    if arg == "24" or kwargs.get("TYPE", "") == "24":
      return time.strftime("%H:%M")
    else:
      return time.strftime("%I:%M %p")

