import subprocess as sp

import automaton.lib.plugin


def platform():
  return ['linux']


# Shuts down the host computer in the specified number of seconds
class Shutdown(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Shutdown, self).__init__(registrar)
    registrar.register_service("shutdown", self.execute,
      grammar={"when": []},
      usage="""
             USAGE: shutdown [when]
             Shuts down the computer at the specified time. Defaults to now.
            """)

  def disable(self):
    self.registrar.unregister_service("shutdown")

  def execute(self, arg='now', **kwargs):
    if "when" not in kwargs:
      kwargs["when"] = "now"
      
    try:
      int(kwargs["when"])
    except ValueError:  # arg is not int
      try:
        if kwargs["when"].find(':') > 0:  # Possibly in hh:mm format
          int(kwargs["when"].split(':')[0]) + int(kwargs["when"].split(':')[1])
        elif kwargs["when"] != 'now':  # Otherwise must be 'now'
          return ''
      except ValueError:
        return ''

    p = sp.Popen('shutdown -P ' + kwargs["when"], stdout=sp.PIPE, shell=True)
    return p.communicate()[0]
