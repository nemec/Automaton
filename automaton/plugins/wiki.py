import subprocess as sp

import automaton.lib.plugin


def platform():
  """Return the list of platforms the plugin is available for."""
  return ['linux', 'mac']


class Wiki(automaton.lib.plugin.PluginInterface):
  """Plugin that retrieves information from a Wikipedia page."""
  def __init__(self, registrar):
    super(Wiki, self).__init__(registrar)
    registrar.register_service("wiki", self.execute,
      grammar={"page": []},
      usage=("USAGE: wiki page\n"
             "Grabs the beginning of the specified wikipedia page."),
      namespace=__name__)

  def disable(self):
    """Disable all of Wiki's services."""
    self.registrar.unregister_service("wiki", namespace=__name__)

  def execute(self, **kwargs):
    """Retrieve the intro text for the given Wikipedia page.

    Keyword arguments:
    page -- the page to request

    """
    if "page" not in kwargs:
      return "No page to look for"

    proc = sp.Popen("dig +short txt \"" + kwargs["page"].replace(" ", "_") +
          ".wp.dg.cx\"", stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    out, err = proc.communicate()
    if len(out) == 0:
      return err
    return out
