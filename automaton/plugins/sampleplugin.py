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
    self.registrar.register_service("converse", self.converse,
                  grammar={"text": []}, usage=usage, namespace=__name__)

  def disable(self):
    """Disable all of SamplePlugin's services."""
    self.registrar.unregister_service("test", namespace=__name__)
    self.registrar.unregister_service("sampleplugin", namespace=__name__)
    self.registrar.unregister_service("converse", namespace=__name__)

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
      ## Call other 
      #command, namespace, args = self.registrar.find_best_service(
      #                                          "echo Hello, {0}".format(name))
      #echo = self.registrar.request_service(command, namespace, args)
      return "Hello, {0}".format(name)
    except ServiceDoesNotExist:
      return "This it thrown when you request a service that is not registered."
    return echo


  def converse(self, **kwargs):
    """Example for using a generator to hold a conversation.
    Allows responding to the user with a request for more information.

    Keyword arguments:
    text -- the text to echo back

    """
    response = yield "And then?"
    yield ("First you said: {0}\n"
        "And then you responded with: {1}".format(
        kwargs.get("text", ""), response["_raw"]))

class SampleTest(automaton.lib.plugin.RegistrationTestCase):
  """Test case describing how to test a plugin."""
  plugin_class = Sample

  # the disable() function is tested automatically by the superclass
  # please do not overwrite test_disable

  def test_grammar(self):
    """Check that the interpreter correctly parses sample input."""
    self.check_interpreter(
      ("test stuff", ("test", __name__, {"title": "stuff"})),
      ("sampleplugin george", ("sampleplugin", __name__, {"title": "george"})),
      ("converse oddly", ("converse", __name__, {"text": "oddly"}))
    )

  def test_exec(self):
    """Test the sample."""
    name = "squirrel"
    self.assertEquals(self.plugin.execute(title=name), "Hello, "+name)

  def test_conversation(self):
    """Test the conversation functionality."""
    start = {'text': "I'm leaving."}
    end = {'_raw': "I'm coming back."}
    self.check_conversation(self.plugin.converse, arg_sequence=(start, end),
      output_sequence=(("And then?", "First you said: {0}\n"
      "And then you responded with: {1}".format(start['text'], end['_raw']))))
