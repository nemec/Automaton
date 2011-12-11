import time
import urllib
import pickle
import httplib2
import simplejson

import automaton.lib.exceptions
import automaton.lib.utils as utils
import automaton.lib.plugin as plugin
import automaton.lib.settings_loader as settings_loader

try:
  from apiclient.discovery import build
except ImportError:
  raise plugin.PluginLoadError(
      "Requires the google-api-python-client to be installed "
      "(http://code.google.com/p/google-api-python-client/)\n"
      "Follow the installation information then try out the Latitude sample.\n"
      "If the sample works, move the latitude.dat file somewhere safe and "
      "modify the cmd_latitude.conf file to point towards that file.")


def platform():
  return ['linux', 'mac', 'windows']


class Latitude(plugin.PluginInterface):

  def __init__(self, registrar):
    super(Latitude, self).__init__(registrar)
    help = """
            USAGE: {0} [noreverse]
            Gets the latitude and longitude from the authenticated
            Google Latitude account and then performs a reverse
            geolookup on it to get the most accurate address
            information for that location. If 'noreverse' is provided
            as an argument or there is no address info for the location,
            the plain latitude and longitude are returned.
           """
    registrar.register_service("latitude", self.execute,
      usage=help.format("latitude"))
    registrar.register_service("location", self.execute,
      usage=help.format("location"))

    utils.spawn_thread(self.location_updater)

  def disable(self):
    self.registrar.unregister_service("latitude")
    self.registrar.unregister_service("location")

  def location_updater(self):
    while True:
      try:
        location = self.execute(noreverse=True)
        self.registrar.register_object("location", location)
        time.sleep(30)
      except plugin.UnsuccessfulExecution:
        pass

  def lookup(self, lat='', lng=''):
    query = urllib.urlencode({'latlng': ','.join((str(lat), str(lng)))})
    url = ('http://maps.googleapis.com/maps/api/geocode/'
            'json?v=1.0&sensor=true&' + query)
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    if len(json['results']) > 0:
      return json['results'][0]['formatted_address']
    else:
      return None

  def execute(self, arg='', **kwargs):
    if arg == "noreverse":
      kwargs["noreverse"] = True
    cmd_op = settings_loader.load_plugin_settings(__name__)
    if not 'AUTHPATH' in cmd_op:
      raise plugin.UnsuccessfulExecution("Server not authenticated "
                                "with Google Latitude.")

    try:
      f = open(cmd_op['AUTHPATH'], "r")
      credentials = pickle.loads(f.read())
      f.close()
    except IOError:
      raise plugin.UnsuccessfulExecution("Error opening authentication file.")

    http = httplib2.Http()
    http = credentials.authorize(http)

    p = build("latitude", "v1", http=http)

    data = p.currentLocation().get(granularity="best").execute()

    if all(k in data for k in ('latitude', 'longitude')):
      if kwargs.get("noreverse", False):
        return "({0}, {1})".format(data['latitude'], data['longitude'])
      else:
        ret = self.lookup(data['latitude'], data['longitude'])
        if ret == None:
          return "({0}, {1})".format(data['latitude'], data['longitude'])
        else:
          return ret
    else:
      if 'kind' in data:
        raise plugin.UnsuccessfulExecution("No latitude data available.")
      else:
        raise plugin.UnsuccessfulExecution("Error in Latitude response.")

  def grammar(self):
    return  ("latitude{\n"
              "keywords = latitude | where | location | address\n"
              "arguments = 0\n"
            "}")
