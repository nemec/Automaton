import automaton.lib.plugin


class Echo(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Echo, self).__init__(registrar)
    registrar.register_service("echo", self.execute,
      grammar={"text":[]},
      usage="USAGE: echo message\nEchoes a message back to the user.",
      namespace=__name__)

  def disable(self):
    self.registrar.unregister_service("echo", namespace=__name__)

  def execute(self, **kwargs):
    return kwargs.get("text", "")

  def help(self):
    return
