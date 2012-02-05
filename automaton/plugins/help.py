import automaton.lib.plugin

class Help(automaton.lib.plugin.PluginInterface):
  """ Help Plugin
      This plugin implements an avenue for searching through existing
      plugins 

  """

  def __init__(self, registrar):
    super(Help, self).__init__(registrar)
    usage = """
            USAGE: %s name
            Prints "hello" along with the provided name
           """
    self.registrar.register_service("help", self.execute,
      grammar={
        "indirect_action": []
        "action": ["me", "us"],
      }, usage=usage, namespace=__name__)
    # Can you help me...
    self.registrar.register_service("do", self.execute,
      grammar={
      
      }, usage=usage, namespace=__name__)
    # What can you do?
    # How do I use...

  def disable(self):
    """Disable all of Help's services."""
    self.registrar.unregister_service("help", namespace=__name__)

  def execute(self, **kwargs):
    """Execute the sample plugin's service.

    Keyword arguments:
    title -- your name (default 'tim')

    """
    
    if "title" in kwargs:
      name = kwargs["title"]
    else:
      name = "tim"
    try:
      return "Hello, {0}".format(name)
    except ServiceDoesNotExist:
      return "This it thrown when you request a service that is not registered."


class HelpTest(automaton.lib.plugin.RegistrationTestCase):
  """Test case describing how to test a plugin."""
  plugin_class = Help

  def test_grammar(self):
    """Check that the interpreter correctly parses sample input."""
    self.check_interpreter(
      ("Can you help me check the weather?",
        ("help", __name__, {"action": "check the weather"})),
      ("How do I use directions?", ("help", __name__, {"action": "directions"})),
      ("What can you do?", ("help", __name__, {"indirect_action": "can you do"}))
    )

#  def test_exec(self):
#    """Test the sample."""
#    name = "squirrel"
#    self.assertEquals(self.plugin.execute(title=name), "Hello, "+name)

#  def test_conversation(self):
#    """Test the conversation functionality."""
#    start = {'text': "I'm leaving."}
#    end = {'_raw': "I'm coming back."}
#    self.check_conversation(self.plugin.converse, arg_sequence=(start, end),
#      output_sequence=(("And then?", "First you said: {0}\n"
#      "And then you responded with: {1}".format(start['text'], end['_raw']))))
