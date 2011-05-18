from automaton.lib.registrar import ServiceDoesNotExist, ObjectDoesNotExist
import automaton.lib.plugin

class Sample(automaton.lib.plugin.PluginInterface):
  """ Sample Plugin
      This plugin defines a working example that can hook into the Automaton
      system.
      It may be called with the syntax "sampleplugin [name]"

  """

  def __init__(self, registrar):
    super(Sample, self).__init__(registrar)
    self.grammar = "*"
    help = """
            USAGE: {0} name
            Prints "hello" along with the provided name
           """
    self.registrar.register_service("test", self.execute, self.grammar, help.format("test"))
    self.registrar.register_service("sampleplugin", self.execute, self.grammar, help.format("sampleplugin"))

  def disable(self):
    self.registrar.remove_service("test")
    self.registrar.remove_service("sampleplugin")


  def fallback_interpreter(self, arg = ''):
    """ Fallback Interpreter
        If the "smart" interpreter is not used on the system, a dictionary
        of keyword arguments will not be created and the raw text will be
        passed straight to the execute function. A fallback interpreter is not
        necessary to define, but helps ensure access to plugins at all times.
        The string can be parsed in any way, but it is usually simpler to prefer
        a more "command line" syntax over natural language.

    """
    kwargs = {}
    if arg is not None and len(arg) > 0:
      kwargs["title"] = arg

    return kwargs


  def execute(self, arg = '', **kwargs):
    if len(kwargs) == 0:
      kwargs = self.fallback_interpreter(arg)
    name = "tim"
    if "title" in kwargs:
      name = kwargs["title"]
    try:
      echo = self.registrar.request_service("echo", "Hello, {0}".format(name))
    except ServiceDoesNotExist:
      return "Please load the echo module before running this program."
    return echo

