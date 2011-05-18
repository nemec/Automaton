import subprocess as sp

import automaton.lib.plugin

def platform():
  return ['linux']

# Shuts down the host computer in the specified number of seconds
class Shutdown(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Shutdown, self).__init__(registrar)
    registrar.register_service("shutdown", self.execute,
      usage = """
               USAGE: shutdown [when]
               Shuts down the computer at the specified time. Defaults to now.
              """)

  def disable(self):
    self.registrar.unregister_service("shutdown")

  def execute(self, arg = 'now'):
      try:
          int(arg)
      except ValueError:  # arg is not int
          try:
              if arg.find(':') > 0: # Possibly in hh:mm format
                  int(arg.split(':')[0])+int(arg.split(':')[1])
              elif not arg == 'now': # Otherwise must be 'now'
                  return ''
          except ValueError:
              return ''        
          
      p = sp.Popen('shutdown -P ' + arg, stdout = sp.PIPE, shell = True)
      return p.communicate()[0]

