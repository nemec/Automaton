try:
  import unittest2 as unittest
except ImportError:
  import unittest

from automaton.lib import registrar


class UnsuccessfulExecution(Exception):
  """ UnsuccessfulExecution errors are not necessarily fatal.
      All they represent is a failure on the service's part to
      successfully produce normal output. For example, if a
      location service is unable to determine an accurate location,
      it can raise this error to let the calling thread know that
      there is no location available.
  """
  pass


class PluginLoadError(Exception):
  pass


class PluginInterface(object):
  def __init__(self, registrar):
    self.registrar = registrar


class RegistrationTestCase(unittest.TestCase):
  """TestCase superclass for plugins.
  Define plugin_type in the subclass and the registrar and plugin will
  be automatically created and destroyed during each test case setup.

  """
  plugin_type = None

  def setUp(self):
    """
    Bind registrar object to self.registrar and plugin object to self.plugin.

    """
    self.registrar = registrar.Registrar()

    self.assertIsNotNone(self.plugin_type, 
      "plugin_type attribute must be defined in subclasses of "
      "RegistrationTestCase.")
    self.plugin = self.plugin_type(self.registrar)

  def test_disable(self):
    """Automated test to ensure disabling a plugin cleans up the registrar."""
    self.plugin.disable()
    self.assertEqual(len(self.registrar.services), 0,
      "Disabling a plugin must remove all registered services.")

  def check_interpreter(self, *args):
    """
    Convenience function for testing the interpreter with a number of
    inputs at once.
    Takes in a variable number of (input, output) pairs, with
      input being the interpreter's input string and
      output being a three-tuple of (service_name, namespace, parsed_arg_dict)
      If any of the output members is None, that output is ignored.

    """
    for inp, out in args:
      out_service, out_namespace, out_args = out
      service, namespace, args = self.registrar.find_best_service(inp)

      if out_service is not None:
        self.assertEquals(service, out_service)
      if out_namespace is not None:
        self.assertEquals(namespace, out_namespace)
      if out_args is not None:
        self.assertEquals(args, out_args)
