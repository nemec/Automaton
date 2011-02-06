class google:

  def execute(self, arg = ''):
      # Requires simplejson module for AJAX search
      # from:http://pypi.python.org/pypi/simplejson
      # Example code found at: http://dcortesi.com/
      import urllib
      import simplejson
      import re
      import unicodedata
      if arg == '':
          return 'Error: No search string.'
      query = urllib.urlencode({'q' : arg})
      url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % (query)
      search_results = urllib.urlopen(url)
      json = simplejson.loads(search_results.read())
      results = json['responseData']['results']
      try:
        ret = re.sub(r'<[^>]*?>', '', results[0]['content']) # Strips HTML formatting
      except:
        return "There was an error parsing data. Please try again."
      ret = re.sub(r'&[^ ]*?;', '', ret) # Strips HTML special characters (ie. &quot; )
      return unicodedata.normalize('NFKD', unicode(ret, "utf-8")).encode('ascii','ignore')
      #return unicodedata.normalize('NFKD', ret).encode('ascii','ignore')

  def grammar(self):
    return  "google{"+\
              "keywords = search | google"+\
              "arguments = *"+\
            "}"

  def platform(self):
    return ['linux', 'mac', 'windows']

  def help(self):
    return """
            USAGE: google query
            The query will be submitted to google, returning the first page of results in text
           """
