import urllib
import simplejson
import httplib2
import pickle
import lib.settings_loader as settings_loader
import lib.Exceptions

try:
  from apiclient.discovery import build
except ImportError:
  print "Requires the google-api-python-client to be installed " +\
        "(http://code.google.com/p/google-api-python-client/)"
  print "Follow the installation information then try out the Latitude sample."
  print "If the sample works, move the latitude.dat file somewhere safe and" +\
        "modify the cmd_latitude.conf file to point towards that file."
  raise lib.Exceptions.ModuleLoadException()

class latitude:
  def lookup(self, lat = '', lng = ''):

    query = urllib.urlencode({'latlng' : ','.join((str(lat),str(lng)))})
    url = 'http://maps.googleapis.com/maps/api/geocode/json?v=1.0&sensor=true&%s' % (query)
    search_results = urllib.urlopen(url)
    json = simplejson.loads(search_results.read())
    if len(json['results']) > 0:
      return json['results'][0]['formatted_address']
    else:
      return None

  def execute(self, arg = ''):
    cmd_op = settings_loader.load_script_settings(__name__)
    if not cmd_op.has_key('AUTHPATH'):
      return "Server not authenticated with Google Latitude."
    
    try:
      f = open(cmd_op['AUTHPATH'], "r")
      credentials = pickle.loads(f.read())
      f.close()
    except IOError:
      return "Error opening authentication file."

    http = httplib2.Http()
    http = credentials.authorize(http)

    p = build("latitude", "v1", http=http)

    data = p.currentLocation().get(granularity="best").execute()

    if data.has_key('latitude') and data.has_key('longitude'):
      if arg == "noreverse":
        return "(%s, %s)" % (data['latitude'], data['longitude'])
      else:
        ret = self.lookup(data['latitude'], data['longitude'])
        if ret == None:
          return "(%s, %s)" % (data['latitude'], data['longitude'])
        else:
          return ret
    else:
      if data.has_key('kind'):
        return "No latitude data available."
      else:
        return "Error in Latitude response."

  def grammar(self):
    return  "latitude{"+\
              "keywords = latitude | where | location | address"+\
              "arguments = 0"+\
            "}"

  def platform(self):
    return ['linux', 'mac', 'windows']

  def help(self):
    return """
            USAGE: latitude [noreverse]
            Gets the latitude and longitude from the authenticated Google Latitude
            account and then performs a reverse geolookup on it to get the most
            accurate address information for that location. If 'noreverse' is
            provided as an argument or there is no address info for the location,
            the plain latitude and longitude are returned.
           """

if __name__=="__main__":
  __name__ = "latitude"
  print "Testing the latitude command"
  l = latitude()
  print l.execute()
  print l.execute("noreverse")
