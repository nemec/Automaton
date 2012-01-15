import time
import urllib
import pickle
import httplib2
import simplejson
import ConfigParser

import automaton.lib.utils as utils
import automaton.lib.plugin as plugin

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
  """Return the list of platforms the plugin is available for."""
  return ['linux', 'mac', 'windows']


class Latitude(plugin.PluginInterface):
  """Plugin that hooks into Google Latitude to grab the user's most recent
  position.

  """
  def __init__(self, registrar):
    super(Latitude, self).__init__(registrar)
    usage = """
            USAGE: %s [noreverse]
            Gets the latitude and longitude from the authenticated
            Google Latitude account and then performs a reverse
            geolookup on it to get the most accurate address
            information for that location. If 'noreverse' is provided
            as an argument or there is no address info for the location,
            the plain latitude and longitude are returned.
           """
    registrar.register_service("latitude", self.execute,
      usage=usage,
      namespace=__name__)
    registrar.register_service("location", self.execute,
      usage=usage,
      namespace=__name__)

    utils.spawn_thread(self.location_updater)

  def disable(self):
    """Disable all of Latitude's services."""
    self.registrar.unregister_service("latitude", namespace=__name__)
    self.registrar.unregister_service("location", namespace=__name__)

  def location_updater(self, pause_seconds=30):
    """Every pause_seconds seconds, attempt to get the current location
    of the user and register it as an object.

    """
    while True:
      try:
        location = self.execute(noreverse=True)
        self.registrar.register_object("location", location)
        time.sleep(pause_seconds)
      except plugin.UnsuccessfulExecution:
        pass

  def lookup(self, lat='', lng=''):
    """Use Google's Map APIs to turn a lat/lon pair into a city."""
    query = urllib.urlencode({'latlng': ','.join((str(lat), str(lng)))})
    url = ('http://maps.googleapis.com/maps/api/geocode/'
            'json?v=1.0&sensor=true&' + query)
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    if len(json['results']) > 0:
      return json['results'][0]['formatted_address']
    else:
      return None

  def execute(self, **kwargs):
    """Log into Google Latitude and retrieve the user's current location.
    
    Keyword arguments:
    noreverse -- Return the latitude and longitude pair rather than turn it
      into a human-readable location. (default False)

    """
    settings = ConfigParser.SafeConfigParser()
    settings.read(utils.get_plugin_settings_paths(__name__))

    try:
      auth = open(settings.get('Settings', 'AUTHPATH'), "r")
      credentials = pickle.loads(auth.read())
      auth.close()
    except ConfigParser.NoSectionError:
      raise plugin.UnsuccessfulExecution("'Settings' section missing from "
                                          "config file.")
    except ConfigParser.NoOptionError:
      raise plugin.UnsuccessfulExecution("Server not authenticated "
                                "with Google Latitude.")
    except IOError:
      raise plugin.UnsuccessfulExecution("Error opening authentication file.")

    http = httplib2.Http()
    http = credentials.authorize(http)

    lat = build("latitude", "v1", http=http)

    data = lat.currentLocation().get(granularity="best").execute()

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
