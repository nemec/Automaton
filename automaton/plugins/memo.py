import ConfigParser
from automaton.lib import logger, plugin, utils


#Inserts your specified text into a "memo" textfile
class Memo(plugin.PluginInterface):
  """Plugin that inserts text into a "memo" textfile."""

  def __init__(self, registrar):
    super(Memo, self).__init__(registrar)

    # Load command settings from a configuration file
    self.settings = ConfigParser.SafeConfigParser()
    self.settings.read(utils.get_plugin_settings_paths(__name__))
    if not self.settings.has_option('Settings', 'memo_file'):
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
        with open(self.settings.get('Settings', 'memo_file'), "a") as fil:
          fil.write(kwargs["memo"] + "\n")
        return "Inserted into memo file."
      except IOError, err:
        logger.log("Error while writing to file", err)
        raise plugin.UnsuccessfulExecution("Error while writing to file.")
    else:
      raise plugin.UnsuccessfulExecution("Must provide data to insert.")
