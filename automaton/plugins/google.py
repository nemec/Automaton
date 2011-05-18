# Requires simplejson module for AJAX search
# from:http://pypi.python.org/pypi/simplejson
# Example code found at: http://dcortesi.com/
import urllib
import simplejson
import re
import unicodedata

import automaton.lib.plugin as plugin

def platform():
  return ['linux', 'mac', 'windows']

class Google(plugin.PluginInterface):

  def __init__(self, registrar):
    super(Google, self).__init__(registrar)
    registrar.register_service("google", self.execute,
      usage = """
               USAGE: google query
               The query will be submitted to google, returning the first page of results in text
              """)

  def disable(self):
    self.registrar.unregister_service("google")

  def execute(self, arg = ''):

      if arg == '':
          raise plugin.UnsuccessfulExecution('Error: No search string.')
      query = urllib.urlencode({'q' : arg})
      url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&' + query
      search_results = urllib.urlopen(url)
      json = simplejson.loads(search_results.read())
      results = json['responseData']['results']
      try:
        ret = re.sub(r'<[^>]*?>', '', results[0]['content']) # Strips HTML formatting
      except:
        raise plugin.UnsuccessfulExecution("There was an error parsing data. Please try again.")
      ret = re.sub(r'&[^ ]*?;', '', ret) # Strips HTML special characters (ie. &quot; )
      return unicodedata.normalize('NFKD', unicode(ret, "utf-8")).encode('ascii','ignore')
      #return unicodedata.normalize('NFKD', ret).encode('ascii','ignore')

  def grammar(self):
    return  "google{"+\
              "keywords = search | google"+\
              "arguments = *"+\
            "}"

