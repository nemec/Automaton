import re
import time
import json
import urllib2
import ConfigParser
from collections import namedtuple
from automaton.lib.data import abbreviations as abbrev
from automaton.lib import logger, plugin, utils


# http://www.wunderground.com/weather/api/d/documentation.html
class Weather(plugin.PluginInterface):
  """Plugin that retrieves weather data for a location."""

  def __init__(self, registrar):
    super(Weather, self).__init__(registrar)
    self.ttl = 3600  # seconds
    self.last = None  # last weather value recorded, tuple of (location, value)
    settings = ConfigParser.SafeConfigParser()
    settings.read(utils.get_plugin_settings_paths(__name__))
    try:
      self.api_key = settings.get("Settings", "wunderground_api_key")
    except ConfigParser.Error:
      raise plugin.PluginLoadError("Must provide "
        "wunderground_api_key in Settings.")
    self.format = 'F'
    try:
      scale = settings.get("Settings", "temp_scale").upper()
      if scale in ('F', 'C', 'K'):
        self.format = scale
    except ConfigParser.Error:
      pass

    self.max_cache_distance = 25
    try:
      self.max_cache_distance = int(settings.get("Settings",
                                                  "max_cache_distance"))
    except (ConfigParser.Error, TypeError):
      pass
    self.CacheItem = namedtuple('CacheItem', ['expires', 'val'])

    self.locations = {}
    try:
      self.locations = dict((key, value) for key, value in
        settings.items("Aliases"))
    except ConfigParser.NoSectionError:
      logger.log("No section 'Aliases' found in weather config file.")

    # remove spaces after commas - these would screw up lat/long searches
    for loc in self.locations:
      self.locations[loc] = re.sub(',\s*', ',', self.locations[loc])
    # dict of location:CacheItem pairs
    # if current time in sec since epoch is less than ttl, cache has expired
    # should return val if cache is still valid
    self.cache = {}
    
    grammar = {
      "when": ["for", "be like"],
      "where": ["at","near","in", 'for'],
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
          yield "Data for {0}: {1}".format(self.last[0], self.last[1].val)
          return
        else:
          self.last = None
      raise plugin.UnsuccessfulExecution("No recent data stored.")

    if "where" not in kwargs:
      try:
        # Try to call on latitude plugin to get the current location
        kwargs["where"] = re.sub("[() ]", "",
                self.registrar.request_service('location', noreverse=True))
      except:
        #raise plugin.UnsuccessfulExecution("No current location is available.")
        kwargs["where"] = (yield "I could not find your current location, "
          "where do you want weather for?")["_raw"]

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
          yield self.cache[location].val
          return
        else:
          self.cache.pop(location, None)

    url = "http://api.wunderground.com/api/{0}/forecast".format(self.api_key)
    query = "/q/{0}.json".format(re.sub('\s+', '_', location))

    resp = json.load(urllib2.urlopen(urllib2.Request(url + query)))
    if not resp:
      raise plugin.UnsuccessfulExecution(
                      "Parsing failed for location " + location)

    ret = None
    if 'results' in resp['response']:
      results = resp['response']['results']
      while len(results) > 1:
        ret = "Did you mean "
        states = set()
        countries = set()
        for result in results:
          if result['state'] != '':
            states.add(result['state'].lower())
          elif result['country'] != '':
            countries.add(result['country'].lower())
        if len(states) > 0:
          ret += "the state"
          if len(states) > 1:
            ret += "s"
          ret += ' ' + utils.humanize_join(
              abbrev.states.try_long(x).capitalize() for x in states)
        if len(countries) > 0:
          if len(states) > 0:
            ret += " or "
          ret += "the country"
          if len(countries) > 1:
            ret += "s"
          ret += ' ' + utils.humanize_join(
              abbrev.countries.try_long(x).capitalize() for x in countries)
        ret += "?"
        # TODO better parsing of conversation arguments
        cont = (yield ret)['_raw'].split()
        old_results = results
        results = []
        for word in cont:
          # Try to convert long name to abbrev
          state = abbrev.states.try_short(word)
          country = abbrev.countries.try_short(word)
          for result in old_results:
            if result['state'].lower() == state.lower():
              results.append(result)
            elif result['country'].lower() == country.lower():
              results.append(result)
        if len(results) == 0:  # Invalid input was given, back up
          results = old_results
      query = results[0]['l'] + '.json'
      resp = json.load(urllib2.urlopen(urllib2.Request(url + query)))
      if not resp:
        raise plugin.UnsuccessfulExecution(
                        "Parsing failed for location " + location)
    try:
      forecast = resp['forecast']['txt_forecast']['forecastday']
      ret = forecast[forecastday]['fcttext']
    except KeyError as err:
      logger.log("Error parsing forecast:", err)

    if not ret:
      raise plugin.UnsuccessfulExecution(
                      "There is no weather data for this location")

    self.last = (location, self.CacheItem(time.time() + self.ttl, ret))
    self.cache[location] = self.last[1]
    yield ret


import unittest
class WeatherTest(plugin.RegistrationTestCase):
  """Test case for the Weather Plugin."""
  plugin_class = Weather

  def test_grammar(self):
    """Check that the interpreter correctly parses sample input."""
    self.check_interpreter(
      ("What is the weather forecast in College Station for tomorrow?",
        ("weather", __name__,
          {'where': "college station", 'when': "tomorrow"}))
    )

    self.check_interpreter(
      ("I would like to know how the weather will be near Houston for today",
        ("weather", __name__,
          {'where': "houston", 'when': "today"}))
    )

    self.check_interpreter(
      ("What will the weather be like tomorrow at Dallas?",
        ("weather", __name__,
          {'where': "dallas", 'when': "tomorrow"}))
    )

    self.check_interpreter(
      ("What is the weather like in Snook?",
        ("weather", __name__,
          {'where': "snook"}))
    )

  @unittest.skip("True distance function is not yet implemented.")
  def test_distance(self):
    """Verify that the distance function calculates correctly."""
    houston = (29.764377375163125, -95.372314453125)
    cstat = (30.64736425824319, -96.3336181640625)
    self.assertAlmostEqual(
      self.plugin.distance(houston, cstat), 53.23, places=7)

  def test_api(self):
    """Test the WeatherUnderground API to ensure it works."""
    out_today = self.plugin.execute(
      where="college station texas", when="today").next()
    self.assertTrue("Highs" in out_today or "Lows" in out_today)
    out_tomorrow = self.plugin.execute(
      where="college station texas", when="tomorrow").next()
    self.assertTrue("Highs" in out_tomorrow or "Lows" in out_tomorrow)

    self.assertNotEquals(out_today, out_tomorrow)

  def test_more_information(self):
    """Test the conversation support when insufficient information provided."""
    out_conv = self.plugin.execute(where="college station", when="tomorrow")
    self.assertTrue(out_conv.next().startswith("Did you mean"))
    final = out_conv.send({'_raw': 'tx'})
    self.assertTrue("Highs" in final or "Lows" in final)
