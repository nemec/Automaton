import time
import re
import urllib2
from xml.dom import minidom

import lib.settings_loader as settings_loader


class cache:
  def __init__(self, ttl, val):
    self.ttl = ttl
    self.val = val

  def __str__(self):
    return "(%s, %s)" % (self.ttl, self.val)

class weather:

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

  def __init__(self):
    self.ttl = 3600 # seconds
    cmd = settings_loader.load_script_settings(self.__class__.__name__)
    self.locations = cmd
    self.format = 'F'
    if self.locations.has_key("FORMAT"):
      if len(self.locations["FORMAT"]) > 0:
        ch = self.locations["FORMAT"][0].upper()
        if ch in ('F', 'C', 'K'):
          self.format = ch
      # We don't want anyone to be able to search for a temp format...
      self.locations.pop("FORMAT", None)

    # remove spaces after commas - these would screw up lat/long searches
    for loc in self.locations:
      self.locations[loc] = re.sub(',\s+',',',self.locations[loc])
    # dict of location:cache pairs
    # if current time in sec since epoch is less than ttl, cache has expired
    # should return val if cache is still valid
    self.cache = {}

  def execute(self, arg=''):
    if arg == '':
      try: # TODO be able to call scripts from within other scripts
        arg = server.call('latitude', '')
      except:
        return "No current location is available."

    arg = arg.upper()
    forecastday = 0

    if arg.endswith("TODAY"):
      arg = arg[0:-len("TODAY")]
      forecastday = 0
    elif arg.endswith("TOMORROW"):
      arg = arg[0:-len("TOMORROW")]
      forecastday = 1
    arg = arg.strip()

    if self.locations.has_key(arg):
      arg = self.locations[arg]

    if self.cache.has_key(arg):
      if time.time() < self.cache[arg].ttl:
        return self.cache[arg].val
      else:
        self.cache.pop(arg, None)

    url = "http://api.wunderground.com/auto/wui/geo/ForecastXML/index.xml?query=%s" % arg

    resp = minidom.parse(urllib2.urlopen(urllib2.Request(url)))
    if resp == None:
      return "Parsing failed for location %s" % arg

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
            ret = 'The weather %s is %s. ' % (self.gettimeofday(), condnode[0].firstChild.data)
        except Exception, e:
          print "Weather", e
          pass

        # Get High, Low Temperatures
        try:
          temp = 0
          t_high = w_node.getElementsByTagName("high")[0]
          if self.format == 'F':
            temp = int(t_high.getElementsByTagName("fahrenheit")[0].firstChild.data)
          else:
            temp = int(t_high.getElementsByTagName("celsius")[0].firstChild.data)
            if format == 'K':
              temp = temp + 273
          ret = ret + 'Highs in the %s %ss. ' % (self.tempmodifier(temp), str(temp-(temp%10)))
          
          t_low = w_node.getElementsByTagName("low")[0]
          if self.format == 'F':
            temp = int(t_low.getElementsByTagName("fahrenheit")[0].firstChild.data)
          else:
            temp = int(t_low.getElementsByTagName("celsius")[0].firstChild.data)
            if format == 'K':
              temp = temp + 273
          ret = ret + 'Lows in the %s %ss. ' % (self.tempmodifier(temp), str(temp-(temp%10)))
        except Exception, e:
          print "Temperature", e
          pass
    except Exception, e:
      print e
      return "Error parsing temperature data."

    if ret == '':
      return "There is no weather data for this location"

    self.cache[arg] = cache(time.time()+self.ttl, ret)

    return ret

  def grammar(self):
    return  "weather{"+\
              "keywords = weather"+\
              "arguments = *"+\
            "}"

  def help(self):
    return """
            USAGE: weather [location|alias]
            Returns the weather for a provided location or alias. If no
            location is provided, gets the weather data for the last
            recorded position.
           """

if __name__=="__main__":
  w = weather()
  print w.execute("school")
