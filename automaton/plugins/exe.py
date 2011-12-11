import subprocess as sp

import automaton.lib.plugin


def platform():
  return ['linux', 'mac', 'windows']


class Exe(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Exe, self).__init__(registrar)
    
    registrar.register_service("exe", self.execute,
      grammar={"command": []},
      usage="""
             USAGE: exe command
             Provide a command that will be executed in a spawned shell.
            """)

  def disable(self):
    self.registrar.unregister_service("exe")

  def execute(self, **kwargs):
    if "command" not in kwargs:
      return "No command entered."
    
    p = sp.Popen(kwargs["command"], stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    out, err = p.communicate()
    if len(out) == 0:
        return err
    return out
