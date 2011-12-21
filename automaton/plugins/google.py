# Requires simplejson module for AJAX search
# from:http://pypi.python.org/pypi/simplejson
# Example code found at: http://dcortesi.com/
import urllib
import simplejson
import re
import unicodedata

import automaton.lib.plugin as plugin


class Google(plugin.PluginInterface):
  """Plugin for searching Google"""

  def __init__(self, registrar):
    super(Google, self).__init__(registrar)
    #registrar.register_service("google", self.execute,
    #  usage="""
    #          USAGE: google query
    #          The query will be submitted to google, returning the first
    #          page of results in text
    #        """)
    
    registrar.register_service("google", self.execute,
      grammar={"query": ["how to"]},
      namespace=__name__)
    registrar.register_service("know", self.execute,
      grammar={"query": ["about"]},
      namespace=__name__)

  def disable(self):
    """Disable all of Google's services."""
    self.registrar.unregister_service("google", namespace=__name__)
    self.registrar.unregister_service("know", namespace=__name__)

  def execute(self, **kwargs):
    """Search Google and return the first result.

    Keyword arguments:
    query -- the query to search for

    """
    if "query" not in kwargs:
      raise plugin.UnsuccessfulExecution('Error: No search string.')
    query = urllib.urlencode({'q': kwargs["query"]})
    url = ('http://ajax.googleapis.com/ajax/services/'
            'search/web?v=1.0&' + query)
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    results = json['responseData']['results']
    try:
      # Strips HTML formatting
      ret = re.sub(r'<[^>]*?>', '', results[0]['content'])
    except:
      raise plugin.UnsuccessfulExecution("There was an error parsing data. "
                                          "Please try again.")

    # Strips HTML special characters (ie. &quot; )
    ret = re.sub(r'&[^ ]*?;', '', ret)

    return unicodedata.normalize('NFKD',
                    unicode(ret, "utf-8")).encode('ascii', 'ignore')
