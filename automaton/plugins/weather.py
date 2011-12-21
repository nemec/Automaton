import time
import re
import urllib2
from xml.dom import minidom
from collections import namedtuple

import automaton.lib.logger as logger
import automaton.lib.plugin as plugin
import automaton.lib.settings_loader as settings_loader


class Weather(plugin.PluginInterface):
  """Plugin that retrieves weather data for a location."""

  def __init__(self, registrar):
    super(Weather, self).__init__(registrar)
    self.ttl = 3600  # seconds
    self.last = None  # last weather value recorded, tuple of (location, value)
    cmd = settings_loader.load_plugin_settings(self.__class__.__name__)
    self.locations = cmd
    self.format = 'F'
    if "FORMAT" in self.locations:
      if len(self.locations["FORMAT"]) > 0:
        temp = self.locations["FORMAT"][0].upper()
        if temp in ('F', 'C', 'K'):
          self.format = temp
      # We don't want anyone to be able to search for a temp format...
      self.locations.pop("FORMAT", None)

    self.max_cache_distance = int(self.locations.pop("MAX_CACHE_DISTANCE", 25))
    self.CacheItem = namedtuple('CacheItem', ['expires', 'val']

    # remove spaces after commas - these would screw up lat/long searches
    for loc in self.locations:
      self.locations[loc] = re.sub(',\s*', ',', self.locations[loc])
    # dict of location:CacheItem pairs
    # if current time in sec since epoch is less than ttl, cache has expired
    # should return val if cache is still valid
    self.cache = {}
    
    grammar = {
      "when": ["for", "be like"],
      "where": ["at","near","in"],
    }

    registrar.register_service("weather", self.execute, grammar=grammar,
      usage="""
             USAGE: %s [location|alias]
             Returns the weather for a provided location or alias. If no
             location is provided, gets the weather data for the last
             recorded position.
            """,
      namespace=__name__)

  def disable(self):
    """Disable all of Weather's services."""
    self.registrar.unregister_service("weather", namespace=__name__)

  def distance(self, src, dest):
    """Compute the distance between src and dest lat/long pairs."""
    # TODO use haversine formula with lat/long to cache close locations?
    # http://www.movable-type.co.uk/scripts/latlong.html
    if src == dest:
      return 0
    else:
      return 100

  def tempmodifier(self, temp):
    """Return whether the ones digit of the temperature is in the low,
    mid, or high range.

    """
    if (temp % 10) < 4:
      return "low"
    elif (temp % 10) < 7:
      return "mid"
    else:
      return "high"

  def gettimeofday(self):
    """Turn a numerical hour into the time of day it corresponds to."""
    hour = time.localtime().tm_hour
    if hour < 3:
      return "tonight"
    elif hour < 12:
      return "this morning"
    elif hour < 7:
      return "today"
    elif hour < 11:
      return "this evening"
    else:
      return "tonight"

  def _parse_response(self, resp, forecastday):
    """Parse the weather response from WUnderground."""
    ret = ''
    try:
      simple = resp.getElementsByTagName("simpleforecast")[0]
      w_list = simple.getElementsByTagName("forecastday")
      if forecastday < len(w_list):
        w_node = w_list[forecastday]

        # Get Weather
        try:
          condnode = w_node.getElementsByTagName("conditions")
          if len(condnode) > 0:
            if forecastday == 1:
              when = "tomorrow"
            else:
              when = self.gettimeofday()
            ret = 'The weather {0} is {1}. '.format(when,
                    condnode[0].firstChild.data)
        except Exception as err:
          logger.log("Exception occurred when parsing Weather", err)

        # Get High, Low Temperatures
        try:
          temp = 0
          for rel_temp in ("high", "low"):
            temp_type = w_node.getElementsByTagName(rel_temp)[0]
            if self.format == 'F':
              temp = int(temp_type.getElementsByTagName(
                                        "fahrenheit")[0].firstChild.data)
            else:
              temp = int(temp_type.getElementsByTagName(
                                        "celsius")[0].firstChild.data)
              if self.format == 'K':
                temp = temp + 273
            ret = ret + '{0}s in the {1} {2}s. '.format(rel_temp.capitalize(),
                                                      self.tempmodifier(temp),
                                                      str(temp - (temp % 10)))
        except Exception as err:
          logger.log("Exception occurred when parsing Weather temp", err)
    except Exception as err:
      logger.log("Error parsing temperature data.", err)
      raise plugin.UnsuccessfulExecution("Error parsing temperature data.")
    return ret

  def execute(self, **kwargs):
    """Retrieve the latest weather for the provided location for the given time.
    
    Keyword arguments:
    last -- if True, return the last retrieved weather data
    where -- the location to get weather data for (defaults to current location)
      Can be an alias (defined in the configuration file)
    when -- one of 'today' or 'tomorrow' (default 'today')

    """
    if kwargs.get("last", None):
      if self.last:
        if time.time() < self.last[1].ttl:
          return "Data for {0}: {1}".format(self.last[0], self.last[1].val)
        else:
          self.last = None
      raise plugin.UnsuccessfulExecution("No recent data stored.")

    if len(kwargs) == 0:
      try:
        # Try to call on latitude plugin to get the current location
        kwargs["where"] = re.sub("[() ]", "",
                self.registrar.request_service('location', 'noreverse'))
      except:
        raise plugin.UnsuccessfulExecution("No current location is available.")

    forecastday = 0
    if "when" in kwargs:
      if kwargs["when"].upper() == "TODAY":
        forecastday = 0
      if kwargs["when"].upper() == "TOMORROW":
        forecastday = 1

    location = kwargs["where"]

    # Sub any aliases
    if location in self.locations:
      location = self.locations[location]

    # Look in the cache, pick item with minimum distance from location, then
    # check to see if it's within the tolerance
    if len(self.cache) > 0:
      cache_hit_distances = ((item, self.distance(location, item))
                              for item in self.cache)
                              
      closest_hit = min(cache_hit_distances, key=lambda x: x[1])[0]
      if closest_hit < self.max_cache_distance:
        if time.time() < self.cache[location].expires:
          return self.cache[location].val
        else:
          self.cache.pop(location, None)

    url = ("http://api.wunderground.com/auto/wui/geo/ForecastXML/"
            "index.xml?query=" + re.sub('\s+', '%20', location))

    resp = minidom.parse(urllib2.urlopen(urllib2.Request(url)))
    if not resp:
      raise plugin.UnsuccessfulExecution(
                      "Parsing failed for location " + location)

    ret = self._parse_response(resp, forecastday)
    if not ret:
      raise plugin.UnsuccessfulExecution(
                      "There is no weather data for this location")

    self.last = (location, self.CacheItem(time.time() + self.ttl, ret))
    self.cache[location] = self.last[1]
    return ret
