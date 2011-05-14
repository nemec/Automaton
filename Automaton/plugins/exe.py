import subprocess as sp

import Automaton.lib.plugin

def platform():
  return ['linux', 'mac', 'windows']

class Exe(Automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Exe, self).__init__(registrar)
    registrar.register_service("exe", self.execute)

  def disable(self):
    self.registrar.unregister_service("exe",
      usage = """
               USAGE: exe command
               Provide a command that will be executed in a spawned shell.
              """)

  def execute(self, arg = ''):
      if arg == '':
          return ''
      p = sp.Popen(arg, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
      out, err = p.communicate()
      if len(out) == 0:
          return err
      return out
