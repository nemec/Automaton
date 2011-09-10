try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.calendar.data
import gdata.calendar.client

import automaton.lib.plugin
import automaton.lib.settings_loader as settings_loader


class Calendar(automaton.lib.plugin.PluginInterface):

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

    registrar.register_service("calendar", self.execute)

  def disable(self):
    self.registrar.unregister_service("calendar")

  def execute(self, arg='', **kwargs):
    pass
