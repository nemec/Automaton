import urllib
import httplib
try:
  import simplejson as json
except ImportError:
  import json
from automaton.lib import exceptions
from automaton.client.base import ClientInterface

class ClientWrapper(ClientInterface):
  """The interface that all clients use to communicate to the server."""
  def __init__(self, server='localhost',
      path_prefix='', port=9090, appname="RESTLib"):
    self.server = server
    self.port = port
    self.appname = appname
    self.clientid = None
    self.prefix = path_prefix

  def get_path(self, _path, _method='GET', **query_args):
    """
    Convenience method for sending a request to the specified path
    with the given HTTP method and query parameters, then parsing the JSON
    response.

    """
    query = urllib.urlencode(query_args)
    page = httplib.HTTPConnection(self.server, self.port)

    if _method.upper() == 'GET':
      req = page.request(_method, "{0}{1}?{2}".format(
        self.prefix, _path, query))
    else:
      headers = {
        "Content-type": "application/x-www-form-urlencoded"
      }
      req = page.request(_method, self.prefix + _path, query, headers)
    resp = page.getresponse()
    content = resp.read()
    response = json.loads(content)
    if "error" in response:
      try:
        error = response["error"]
        if error.get("code") == 500:
          etype = getattr(exceptions, error["kind"], None)
          if etype:  # Exception type exists
            raise etype(error["description"])
          else:
            raise exceptions.ClientError(response)
        else:
          raise exceptions.ClientError(error['code'], error['description'])
      except AttributeError as err:
        raise (exceptions.ClientError(
          "Could not parse error condition.", response))
    if "data" in response:
      return response["data"]
    else:
      raise exceptions.ClientError("No data was returned in a response",
        response)

  def open(self):
    """Open a connection to the server and register the client."""
    response = self.get_path('/register', _method='POST', appname=self.appname)
    try:
      self.clientid = response['uh']
    except KeyError:
      raise exceptions.ClientError(
        "User Hash (uh) not present in registration response: " + str(response))

  def close(self):
    """Unregister from the server."""
    self.get_path('/unregister', _method='POST', uh=self.clientid)
    self.clientid = None

  def getAvailableServices(self):
    """List the available services on the server."""
    return self.get_path('/services', _method="GET")

  def isService(self, name):
    return {"error": {
      "kind": "DeprecationWarning",
      "description": "This method is deprecated. Use findServices instead."
    }}

  def findServices(self, query):
    """
    Parse the given query and return a list of dicts containing
    matched services' names and namespaces.

    """
    return self.get_path('/services/find', _method='GET', q=query)

  def allowService(self, name):
    """Enable the given service to be used by the client."""
    return self.get_path('/services/allow', _method='POST',
      uh=self.clientid, service=name)

  def disallowService(self, name):
    """Stop the given service from being able to be called by the client."""
    return self.get_path('/services/disallow', _method='POST',
      uh=self.clientid, service=name)

  def allowAllServices(self):
    """Make every service available to be called."""
    return self.get_path('/services/allow', _method='POST',
      uh=self.clientid, all=1)

  def disallowAllServices(self):
    """Disallow any service from being called."""
    return self.get_path('/services/disallow', _method='POST',
      uh=self.clientid, all=1)

  def interpret(self, raw):
    """Parse the given query and return its response."""
    return self.get_path('/services/interpret', _method='GET',
      uh=self.clientid, q=raw)

  def serviceUsage(self, name):
    """Return help text for the given service."""
    return self.get_path('/services/help', _method='GET', service=name)
