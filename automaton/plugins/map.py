import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json
import unicodedata
import re

import automaton.lib.plugin as plugin


class Map(plugin.PluginInterface):

  def __init__(self, registrar):
    super(Map, self).__init__(registrar)
    
    usage = ("USAGE: {0} [origin] to [destination]\n"
             "Returns text directions from origin to destination from GMaps")
    
    grammar = {"to":["ending at", "to"], "from":[ "starting at", "from"]}
    
    registrar.register_service("map", self.interpret,
      grammar=grammar, usage=usage.format("map"), namespace=__name__)
    registrar.register_service("directions", self.interpret,
      grammar=grammar, usage=usage.format("directions"), namespace=__name__)

  def disable(self):
    self.registrar.unregister_service("map", namespace=__name__)
    self.registrar.unregister_service("directions", namespace=__name__)

  #def execute(self, arg=''):
  #  if arg == '':
  #    return self.help()

  #  arg = re.sub(r'^from', '', arg)

  #  origin, sep, destination = arg.partition(" to ")
  #  if sep == '':
  #    destination = arg
  #    destination = re.sub("^to ", "", destination)
  #    origin = ''
  #  return self.interpret(TO=origin, FROM=destination)

  def interpret(self, arg='', **kwargs):
    if "to" not in kwargs:
      return "Please provide a destination."
      
    origin = kwargs.get("from", '')
    destination = kwargs["to"]
    
    if origin == '':
      try:
        origin = self.registrar.request_service('latitude')
      except Exception as e:
        print e
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
      steps = response['Directions']['Routes'][0]['Steps']
      ret = ""
      for line in steps:
        ret = (ret + line['descriptionHtml'] +
                ' for ' + line['Distance']['html'] + '\n')
        # Strips HTML tags
        ret = re.sub(r'<.*?>', '', ret)
        # Strips HTML special characters (ie. &quot; )
        ret = re.sub(r'&[^ ]*?;', '', ret)
      return ret.rstrip()
    elif status_code == 602:
      raise plugin.UnsuccessfulExecution('malformed query')
    raise plugin.UnsuccessfulExecution("Unknown status code: " + status_code)
