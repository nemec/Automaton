import subprocess as sp

import automaton.lib.plugin


class Exe(automaton.lib.plugin.PluginInterface):
  """Execute an arbitrary command through the system's command line."""
  def __init__(self, registrar):
    super(Exe, self).__init__(registrar)
    
    registrar.register_service("exe", self.execute,
      grammar={"command": []},
      usage="USAGE: %s command\n"
            "Provide a command that will be executed in a spawned shell.",
      namespace=__name__)

  def disable(self):
    """Disable all of Exe's services."""
    self.registrar.unregister_service("exe", namespace=__name__)

  def execute(self, **kwargs):
    """Execute an arbitrary command through the system command line."

    Keyword arguments:
    command -- the command to execute

    """
    if "command" not in kwargs:
      return "No command entered."
    
    proc = sp.Popen(kwargs["command"], stdout=sp.PIPE,
                    stderr=sp.PIPE, shell=True)
    out, err = proc.communicate()
    if len(out) == 0:
      return err
    return out
