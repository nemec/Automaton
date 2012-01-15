import automaton.lib.plugin


class Echo(automaton.lib.plugin.PluginInterface):
  """Plugin that echoes the input back as output."""
  def __init__(self, registrar):
    super(Echo, self).__init__(registrar)
    registrar.register_service("echo", self.execute,
      grammar={"text":[]},
      usage="USAGE: %s message\nEchoes a message back to the user.",
      namespace=__name__)

  def disable(self):
    """Disable all of Echo's services."""
    self.registrar.unregister_service("echo", namespace=__name__)

  def execute(self, **kwargs):
    """Return the input text back to the caller.

    Keyword arguments:
    text -- the text to echo back

    """
    return kwargs.get("text", "")

class EchoTest(automaton.lib.plugin.RegistrationTestCase):
  """Test case for the Echo plugin."""
  plugin_class = Echo

  def test_grammar(self):
    """Check that the interpreter correctly parses sample input."""
    self.check_interpreter(
      ("echo hello world", ("echo", __name__, {"text": "hello world"}))
    )

  def test_echo(self):
    """Test the echo function."""
    message = "Hello world."
    self.assertEquals(message, self.plugin.execute(text=message))
