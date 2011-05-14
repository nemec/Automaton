import urllib
import urllib2
try:
    import json
except ImportError:
    import simplejson as json
import unicodedata
import re

import Automaton.lib.plugin

class Map(Automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Map, self).__init__(registrar)
    registrar.register_service("map", self.execute,
      usage = """
               USAGE: map [origin] to [destination]
               Returns text directions from origin to destination from GMaps
              """)

  def disable(self):
    self.registrar.unregister_service("map")

  def execute(self, arg = ''):
    if arg == '':
      return self.help()

    arg = re.sub(r'^from', '', arg)

    origin, sep, destination = arg.partition(" to ")
    if sep == '':
      destination = arg
      destination = re.sub("^to ", "", destination)
      origin = ''

    if origin == '':
      try:
        origin = self.registrar.request_service('latitude')
      except Exception as e:
        print e
        return "Could not determine location."

    params = {
      'q':        'from:{0} to:{1}'.format(origin, destination),
      'output':   'json',
      'oe':       'utf8',
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
        ret = ret + line['descriptionHtml'] + ' for ' + line['Distance']['html'] + '\n'
        ret = re.sub(r'<.*?>', '', ret) # Strips HTML tags
        ret = re.sub(r'&[^ ]*?;', '', ret) # Strips HTML special characters (ie. &quot; )
      return ret.rstrip()
    elif status_code == 602:
      return 'malformed query'

  def grammar(self):
    return  "map{"+\
              "keywords = map | directions | direction | navigate"+\
              "arguments = *"+\
            "}"

