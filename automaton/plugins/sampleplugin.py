# pylint: disable-msg=W0611
from automaton.lib.registrar import ServiceDoesNotExist, ObjectDoesNotExist
import automaton.lib.plugin

try:
  pass
except ImportError:
  raise automaton.lib.plugin.PluginLoadError(
    "Raise this exception if something bad can happen when loading "
    "the plugin. Plugin is not enabled if an exception is raised when loading.")



class Sample(automaton.lib.plugin.PluginInterface):
  """ Sample Plugin
      This plugin defines a working example that can hook into the Automaton
      system.

  """

  def __init__(self, registrar):
    super(Sample, self).__init__(registrar)
    grammar = {
      "title": [],
    }
    usage = """
            USAGE: %s name
            Prints "hello" along with the provided name
           """
    self.registrar.register_service("test", self.execute,
                  grammar=grammar, usage=usage, namespace=__name__)
    self.registrar.register_service("sampleplugin", self.execute,
                  grammar=grammar, usage=usage, namespace=__name__)

  def disable(self):
    """Disable all of SamplePlugin's services."""
    self.registrar.remove_service("test", namespace=__name__)
    self.registrar.remove_service("sampleplugin", namespace=__name__)

  def execute(self, **kwargs):
    """Execute the sample plugin's service.

    Keyword arguments:
    title -- your name (default 'tim')

    """
    
    def callback(obj):
      """Called whenever "cool stuff" is updated."""
      print obj
    
    self.registrar.register_object_listener("cool stuff", callback)
    
    if "title" in kwargs:
      name = kwargs["title"]
    else:
      name = "tim"
    try:
      command, namespace, args = self.registrar.find_best_service(
                                                "echo Hello, {0}".format(name))
      echo = self.registrar.request_service(command, namespace, args)
    except ServiceDoesNotExist:
      return "Please load the echo module before running this program."
    return echo
