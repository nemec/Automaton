import re
import subprocess as sp

import Automaton.lib.plugin

def platform():
  return ['linux', 'mac']

class Wiki(Automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Wiki, self).__init__(registrar)
    registrar.register_service("wiki", self.execute,
      usage = """
               USAGE: wiki page
               Grabs the beginning of the specified wikipedia page.
              """)

  def disable(self):
    self.registrar.unregister_service("wiki")

  def execute(self, arg = '', **kwargs):
    if arg == '':
      return ''

    p = sp.Popen("dig +short txt \""+arg.replace(" ", "_")+".wp.dg.cx\"", stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
    out, err = p.communicate()
    if len(out) == 0:
        return err
    return out

if __name__ == "__main__":
  import Automaton.lib.registrar as registrar
  r = registrar.Registrar()
  w = Wiki(r)
  print w.execute("hello")
