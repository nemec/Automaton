import urllib
import urllib2
try:
  import json
except ImportError:
  import simplejson as json
import re

import automaton.lib.plugin as plugin
import automaton.lib.logger as logger


class Map(plugin.PluginInterface):
  """Plugin that retrieves directions from Google Maps."""

  def __init__(self, registrar):
    super(Map, self).__init__(registrar)

    usage = ("USAGE: %s [origin] to [destination]\n"
             "Returns text directions from origin to destination from GMaps")

    grammar = {"to":["ending at", "to"], "from":[ "starting at", "from"]}

    registrar.register_service("map", self.interpret,
      grammar=grammar, usage=usage, namespace=__name__)
    registrar.register_service("directions", self.interpret,
      grammar=grammar, usage=usage, namespace=__name__)

  def disable(self):
    """Disable all of Map's services."""
    self.registrar.unregister_service("map", namespace=__name__)
    self.registrar.unregister_service("directions", namespace=__name__)

  def format_directions_for_human(self, steps):
    """Format the given steps in a human-readable manner."""
    ret = ""
    for line in steps:
      ret = (ret + line['descriptionHtml'] +
              ' for ' + line['Distance']['html'] + '\n')
      # Strips HTML tags
      ret = re.sub(r'<.*?>', '', ret)
      # Strips HTML special characters (ie. &quot; )
      ret = re.sub(r'&[^ ]*?;', '', ret)
    return ret.rstrip()

  def interpret(self, arg='', **kwargs):
    """Retrieve directions from Google Maps and format them in a
       human-readable manner.

    Keyword arguments:
    to -- the destination address
    from -- the source address (default: current location, if available)

    """
    if "to" not in kwargs:
      return "Please provide a destination."
      
    origin = kwargs.get("from", '')
    destination = kwargs["to"]
    
    if origin == '':
      try:
        origin = self.registrar.request_service(
          *self.registrar.find_best_service('location'))
      except Exception as error:
        logger.log("Could not determine location", error)
        raise plugin.UnsuccessfulExecution("Could not determine location.")

    params = {
      'q': 'from:{0} to:{1}'.format(origin, destination),
      'output': 'json',
      'oe': 'utf8',
    }

    encoded_params = urllib.urlencode(params)
    url = 'http://maps.google.com/maps/nav?' + encoded_params
    request = urllib2.Request(url)
    resp = urllib2.urlopen(request)
    response = json.load(resp)

    status_code = response['Status']['code']
    if status_code == 200:
      return self.format_directions_for_human(
        response['Directions']['Routes'][0]['Steps'])
    elif status_code == 602:
      raise plugin.UnsuccessfulExecution('malformed query')
    raise plugin.UnsuccessfulExecution("Unknown status code: " + status_code)
