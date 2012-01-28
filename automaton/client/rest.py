import urllib
import urllib2
try:
  import simplejson as json
except ImportError:
  import json
import automaton.lib.exceptions
from automaton.client.base import ClientInterface

class ClientWrapper(ClientInterface):
  """The interface that all clients use to communicate to the server."""
  def __init__(self, server='localhost',
      path_prefix='/automaton', port=9090, appname="RESTLib"):
    self.appname = appname
    self.clientid = None
    self.prefix = path_prefix

  def get_path(self, _path, _suppress_err=False, **query_args):
    query = urllib.urlencode({'q': kwargs["query"]})
    page = urllib2.urlopen('http://{0}:{1}/{2}{3}?{4}'.format(
      self.server, self.port, self.path_prefix, _path, query))
    response = json.loads(page.read())
    if not _suppress_err:
      if "error" in response:
        try:
          if response["error"].get("code") == '500':
            etype = getattr(
              automaton.lib.exceptions, response["error"]["kind"], None)
            if etype:  # Exception type exists
              raise etype(response["error"]["description"])
            else:
              raise automaton.lib.ClientError(
        except AttributeError as err:
          raise (automaton.lib.ClientError(
            "Could not parse error condition.", response) from err)
    

  # Opens a connection to the server and registers the client
  def open(self):
    response = self.get_path('/register', self.appname)
    self.clientid = None

  # Unregisters from the server then closes the connection
  def close(self):
    self.clientid = None

  def getAvailableServices(self):
    return self.client.getAvailableServices()

  def isService(self, name):
    return self.client.isService(name)

  def allowService(self, name):
    return self.client.allowService(self.clientid, name)

  def disallowService(self, name):
    return self.client.disallowService(self.clientid, name)

  def allowAllServices(self):
    return self.client.allowAllServices(self.clientid)

  def disallowAllServices(self):
    return self.client.disallowAllServices(self.clientid)

  def interpret(self, raw):
    return self.client.interpret(self.clientid, raw)

  def serviceUsage(self, name):
    return self.client.serviceUsage(name)
