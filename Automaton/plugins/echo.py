import Automaton.lib.plugin

class Echo(Automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Echo, self).__init__(registrar)
    registrar.register_service("echo", self.execute)

  def disable(self):
    self.registrar.unregister_service("echo",
      usage = """
               USAGE: echo message
               Echoes a message back to the user.
              """)

  def execute(self, arg = ''):
    return arg

  def grammar(self):
    return  "echo{"+\
              "keywords = echo | repeat"+\
              "arguments = *"+\
            "}"

  def help(self):
    return 
