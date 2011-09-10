import automaton.lib.plugin as plugin
import automaton.lib.settings_loader as settings_loader


def platform():
  return ['linux', 'mac', 'windows']


#Inserts your specified text into a "memo" textfile
class Memo(plugin.PluginInterface):

  def __init__(self, registrar):
    super(Memo, self).__init__(registrar)
    registrar.register_service("memo", self.execute,
      usage="""
             USAGE: memo message
             Appends message to the file specified in the configuration file.
            """)

  def disable(self):
    self.registrar.unregister_service("memo")

  def execute(self, arg=''):
    # Load command settings from a configuration file
    cmd_op = settings_loader.load_plugin_settings(__name__)
    if "MEMO_FILE" not in cmd_op:
      raise plugin.UnsuccessfulExecution(
          "Error: no memo file provided in the config.")
    f = open(cmd_op['MEMO_FILE'], "a")
    if arg != '':
        f.write(arg + "\n")
    f.close()
    return "Inserted into memo file."
