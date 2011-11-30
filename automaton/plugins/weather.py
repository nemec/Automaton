import time
import re
import urllib2
from xml.dom import minidom

import automaton.lib.plugin as plugin
import automaton.lib.settings_loader as settings_loader


class cache:
  def __init__(self, ttl, val):
    self.ttl = ttl
    self.val = val

  def __str__(self):
    return "({0}, {1})".format(self.ttl, self.val)


class Weather(plugin.PluginInterface):

  def __init__(self, registrar):
    super(Weather, self).__init__(registrar)
    self.ttl = 3600  # seconds
    self.last = None  # last weather value recorded, tuple of (location, value)
    cmd = settings_loader.load_plugin_settings(self.__class__.__name__)
    self.locations = cmd
    self.format = 'F'
    if "FORMAT" in self.locations:
      if len(self.locations["FORMAT"]) > 0:
        ch = self.locations["FORMAT"][0].upper()
        if ch in ('F', 'C', 'K'):
          self.format = ch
      # We don't want anyone to be able to search for a temp format...
      self.locations.pop("FORMAT", None)

    # remove spaces after commas - these would screw up lat/long searches
    for loc in self.locations:
      self.locations[loc] = re.sub(',\s*', ',', self.locations[loc])
    # dict of location:cache pairs
    # if current time in sec since epoch is less than ttl, cache has expired
    # should return val if cache is still valid
    self.cache = {}
    
    grammar = {
      "when": ["for", "be like"],
      "where": ["at","near","in"],
    }

    registrar.register_service("weather", self.execute, grammar=grammar,
      usage="""
             USAGE: weather [location|alias]
             Returns the weather for a provided location or alias. If no
             location is provided, gets the weather data for the last
             recorded position.
            """)

  def disable(self):
    self.registrar.unregister_service("weather")

  def distance(a, b):
    # TODO use haversine formula with lat/long to cache close locations?
    # http://www.movable-type.co.uk/scripts/latlong.html
    return a == b

  def tempmodifier(self, temp):
    if (temp % 10) < 4:
      return "low"
    elif (temp % 10) < 7:
      return "mid"
    else:
      return "high"

  def gettimeofday(self):
    hr = time.localtime().tm_hour
    if hr < 3:
      return "tonight"
    elif hr < 12:
      return "this morning"
    elif hr < 7:
      return "today"
    elif hr < 11:
      return "this evening"
    else:
      return "tonight"

  def parse_response(self, resp, forecastday):
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
              time = "tomorrow"
            else:
              time = self.gettimeofday()
            ret = 'The weather {0} is {1}. '.format(time,
                    condnode[0].firstChild.data)
        except Exception as e:
          print "Weather ", e
          pass

        # Get High, Low Temperatures
        try:
          temp = 0
          t_high = w_node.getElementsByTagName("high")[0]
          if self.format == 'F':
            temp = int(t_high.getElementsByTagName(
                                      "fahrenheit")[0].firstChild.data)
          else:
            temp = int(t_high.getElementsByTagName(
                                      "celsius")[0].firstChild.data)
            if self.format == 'K':
              temp = temp + 273
          ret = ret + 'Highs in the {0} {1}s. '.format(self.tempmodifier(temp),
                                                      str(temp - (temp % 10)))

          t_low = w_node.getElementsByTagName("low")[0]
          if self.format == 'F':
            temp = int(t_low.getElementsByTagName(
                                      "fahrenheit")[0].firstChild.data)
          else:
            temp = int(t_low.getElementsByTagName(
                                      "celsius")[0].firstChild.data)
            if self.format == 'K':
              temp = temp + 273
          ret = ret + 'Lows in the {0} {1}s. '.format(self.tempmodifier(temp),
                                                      str(temp - (temp % 10)))
        except Exception as e:
          print "Temperature", e
          pass
    except Exception as e:
      print e
      raise plugin.UnsuccessfulExecution("Error parsing temperature data.")

    return ret

  def fallback_interpreter(self, arg=None):
    if not arg:
      return {}

    arg = arg.upper()

    if arg == "last":
      return {"last": True}

    kwargs = {}
    if arg.endswith("TOMORROW"):
      kwargs["when"] = "TOMORROW"
      arg = arg[:-len("TOMORROW")].strip()

    if arg.startswith("at") or arg.startswith("in"):
      arg = arg[len("at") + 1:].strip()

    kwargs["where"] = arg

    return kwargs

  def execute(self, arg=None, **kwargs):
    if len(kwargs) == 0:
      kwargs = self.fallback_interpreter(arg)

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
      if kwargs["when"] == "TODAY":
        forecastday = 0
      if kwargs["when"] == "TOMORROW":
        forecastday = 1

    location = kwargs["where"]

    # Sub any aliases
    if location in self.locations:
      location = self.locations[location]

    # Look in the cache
    # @TODO compute distance between all locations in cache before comparing
    if location in self.cache:
      if time.time() < self.cache[location].ttl:
        return self.cache[location].val
      else:
        self.cache.pop(location, None)

    url = ("http://api.wunderground.com/auto/wui/geo/ForecastXML/"
            "index.xml?query=" + re.sub('\s+', '%20', location))

    resp = minidom.parse(urllib2.urlopen(urllib2.Request(url)))
    if resp == None:
      raise plugin.UnsuccessfulExecution(
                      "Parsing failed for location " + location)

    ret = self.parse_response(resp, forecastday)

    if ret == '':
      raise plugin.UnsuccessfulExecution(
                      "There is no weather data for this location")

    self.last = (location, cache(time.time() + self.ttl, ret))
    self.cache[location] = self.last[1]

    return ret
