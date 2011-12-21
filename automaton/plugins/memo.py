import automaton.lib.logger as logger
import automaton.lib.plugin as plugin
import automaton.lib.settings_loader as settings_loader


#Inserts your specified text into a "memo" textfile
class Memo(plugin.PluginInterface):
  """Plugin that inserts text into a "memo" textfile."""

  def __init__(self, registrar):
    super(Memo, self).__init__(registrar)

    # Load command settings from a configuration file
    self.cmd_op = settings_loader.load_plugin_settings(__name__)
    if "MEMO_FILE" not in self.cmd_op:
      raise plugin.PluginLoadError(
          "Error: no memo file provided in the config.")

    usage = ("USAGE: %s message\n"
             "Appends message to the file specified "
             "in the configuration file.")

    registrar.register_service("memo", self.execute,
      grammar={"memo": []}, usage=usage, namespace=__name__)

    registrar.register_service("remember", self.execute,
      grammar={"memo": []}, usage=usage, namespace=__name__)

  def disable(self):
    """Disable all of Memo's services."""
    self.registrar.unregister_service("memo", namespace=__name__)
    self.registrar.unregister_service("remember", namespace=__name__)

  def execute(self, **kwargs):
    """Insert memo text as a new line in the memo file.

    Keyword arguments:
    memo -- the text to insert into the memo file

    """
    if "memo" in kwargs:
      try:
        with open(self.cmd_op['MEMO_FILE'], "a") as fil:
          fil.write(kwargs["memo"] + "\n")
        return "Inserted into memo file."
      except IOError, err:
        logger.log("Error while writing to file", err)
        raise plugin.UnsuccessfulExecution("Error while writing to file.")
    else:
      raise plugin.UnsuccessfulExecution("Must provide data to insert.")
