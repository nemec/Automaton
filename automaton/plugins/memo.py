import automaton.lib.plugin as plugin
import automaton.lib.settings_loader as settings_loader


def platform():
  return ['linux', 'mac', 'windows']


#Inserts your specified text into a "memo" textfile
class Memo(plugin.PluginInterface):

  def __init__(self, registrar):
    super(Memo, self).__init__(registrar)
    
    # Load command settings from a configuration file
    self.cmd_op = settings_loader.load_plugin_settings(__name__)
    if "MEMO_FILE" not in self.cmd_op:
      raise plugin.PluginLoadError(
          "Error: no memo file provided in the config.")
    
    registrar.register_service("memo", self.execute,
      grammar={"memo": []},
      usage=("USAGE: memo message\n"
             "Appends message to the file specified "
             "in the configuration file."),
      namespace=__name__)
    
    registrar.register_service("remember", self.execute,
      grammar={"memo": []},
      usage=("USAGE: remember message\n"
             "Appends message to the file specified "
             "in the configuration file."),
      namespace=__name__)

  def disable(self):
    self.registrar.unregister_service("memo", namespace=__name__)
    self.registrar.unregister_service("remember", namespace=__name__)

  def execute(self, **kwargs):
    f = open(self.cmd_op['MEMO_FILE'], "a")
    if "memo" in kwargs:
        f.write(kwargs["memo"] + "\n")
    f.close()
    return "Inserted into memo file."
