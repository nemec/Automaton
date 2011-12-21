import gdata.calendar.data
import gdata.calendar.client

import automaton.lib.plugin
import automaton.lib.settings_loader as settings_loader

# pylint: disable-msg=W0101
raise automaton.lib.plugin.PluginLoadError("Incomplete plugin. "
  "Loading has no effect.")


class Calendar(automaton.lib.plugin.PluginInterface):
  """Plugin that allows access to a Google Calendar."""
  def __init__(self, registrar):
    super(Calendar, self).__init__(registrar)
    self.settings = settings_loader.load_plugin_settings(
                                                      self.__class__.__name__)
    if "EMAIL" not in self.settings and "PASSWORD" not in self.settings:
      raise Exception("Email and password required to load calendar.")

    self.cal_client = gdata.calendar.client.CalendarClient(
                                        source='Automaton-CalendarPlugin-0.1')
    self.cal_client.ClientLogin(self.settings["EMAIL"],
                                self.settings["PASSWORD"],
                                self.cal_client.source)

  def disable(self):
    """Disable all of Calendar's services."""
    pass
