import re
import subprocess as sp

import automaton.lib.plugin


def platform():
  return ['linux', 'mac']


class Wiki(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Wiki, self).__init__(registrar)
    registrar.register_service("wiki", self.execute,
      grammar={"page": []},
      usage="""
             USAGE: wiki page
             Grabs the beginning of the specified wikipedia page.
            """)

  def disable(self):
    self.registrar.unregister_service("wiki")
    
  def fallback_interpreter(self, arg=''):
    return self.execute(PAGE=arg)

  def execute(self, arg='', **kwargs):
    if "PAGE" not in kwargs:
      return "No page to look for"

    p = sp.Popen("dig +short txt \"" + kwargs["PAGE"].replace(" ", "_") + ".wp.dg.cx\"",
          stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    out, err = p.communicate()
    if len(out) == 0:
        return err
    return out

if __name__ == "__main__":
  import automaton.lib.registrar as registrar
  r = registrar.Registrar()
  w = Wiki(r)
  print w.fallback_interpreter("hello")
