import cherrypy
from cherrypy import tools
try:
  import simplejson as json
except ImportError:
  import json

from automaton.server.base import AutomatonServer
from automaton.lib import exceptions, logger


class Root(object):
  pass
root = Root()


class Register(object):
  exposed = True
  def __init__(self, server):
    self.server = server

  @tools.json_out()
  def POST(self, appname="RESTLib", **kwargs):
    """Proxy for AutomatonServer's registerClient method.
    path: /register
    parameters:
      appname -- An identifier for the client. Prepended to a UID for
                  human-readable identification of clients.
    sample response:
      {
        "data": {
          "uh": "my-app-4B82-A72D-2338"
        }
      }

    """
    uh = self.server.registerClient(appname=appname)
    return {
      "data": {
        "uh": uh
      }
    }


class Unregister(object):
  exposed = True
  def __init__(self, server):
    self.server = server
  
  @tools.json_out()
  def POST(self, uh, **kwargs):
    self.server.unregisterClient(uh)
    return {"data": ""}


class Services(object):
  exposed = True
  def __init__(self, server):
    self.server = server
    
    for api in ('Allow', 'Deny', 'Interpret', 'Find', 'Help'):
      cls = getattr(self, api)
      setattr(self, api.lower(), cls())
      cls.server = server
#    self.allow = self.Allow()
#    self.deny = self.Deny()
#    self.interpret = self.Interpret()
#    self.
#    
#    self.allow.server = server
#    self.deny.server = server
#    self.interpret.server = server
#    self.find.server = server

  @tools.json_out()
  def GET(self, **kwargs):
    return {
      "data": self.server.getAvailableServices()
    }

  class Allow(object):
    exposed = True

    @tools.json_out()
    def POST(self, uh, service=None, all=False, **kwargs):
      if all is not False:  # Empty string also counts as 'all'
        self.server.allowAllServices(uh)
      else:
        self.server.allowService(uh, service)
      return {"data": ""}

  class Deny(object):
    exposed = True
    
    @tools.json_out()
    def POST(self, uh, service=None, all=False, **kwargs):
      if all is not False:
        self.server.disallowAllServices(uh)
      else:
        self.server.disallowService(uh, service)
      return {"data": ""}

  class Interpret(object):
    exposed = True
    
    @tools.json_out()
    def GET(self, uh, q=None, **kwargs):
      return {
        "data": self.server.interpret(uh, q)
      }

  class Find(object):
    exposed = True
    
    @tools.json_out()
    def GET(self, q, **kwargs):
      data = []
      for service, namespace, args in self.server.findServices(q):
        data.append({"service": service, "namespace": namespace})
      return {
        "data": data
      }

  class Help(object):
    exposed = True

    @tools.json_out()
    def GET(self, service, **kwargs):
      return {
        "data": self.server.serviceUsage(service)
      }

class CherryServer(AutomatonServer):
  """Wrapper for building the AutomatonServer with CherryPy."""
  base_path = '/'

  def __init__(self, withgui=False, port=9090):
    AutomatonServer.__init__(self, withgui)
    self.port = port
    self.encoder = json.JSONEncoder()

  def initialize(self):
    """Initialize CherryPy routes and exception handling."""
    root.register = Register(self)
    root.unregister = Unregister(self)
    root.services = Services(self)
    
    cherrypy.config.update({
      'server.socket_host': '127.0.0.1',
      'server.socket_port': self.port,
      'request.error_response': self.handle_error,
      'error_page.404': self.make_error_dict
    })

  def _start(self):
    cherrypy.quickstart(root=root, config={
      '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
      }
    })

  def make_error_dict(self, status, message, traceback=None,
                      version=None, kind=None):
    try:
      status, sep, end = status.partition(' ')
    except AttributeError:
      pass
    try:
      status = int(status)
    except ValueError:
      pass
    err_dict = {
      "code": status,
      "description": message,
    }
    if kind:
      err_dict["kind"] = kind
    return self.encoder.iterencode({
      "error": err_dict
    })

  def handle_error(self):
    import sys, traceback
    exc_type, exc_value, exc_traceback = sys.exc_info()
    cherrypy.response.status = 500
    logger.log(''.join(traceback.format_exception(
      exc_type, exc_value, exc_traceback)))
    cherrypy.response.headers['Content-Type'] = 'application/json'
    try:
      cherrypy.response.body = [''.join(self.make_error_dict(
        500, "Unexpected exception occurred during execution.",
        kind=exc_type.__name__))]
    except Exception as err:
      print err
      err = cherrypy._cperror.bare_error()
      status = err[0]
      message = '\n'.join(err[2])
      cherrypy.response.body = [''.join(self.make_error_dict(status, message))]

  @tools.json_out()
  def allow_service(self, uh, name, *args, **kwargs):
    """Proxy for AutomatonServer's allowService method.
    path: /services/allow
    parameters:
      uh -- The id identifying the client, returned from /register.
      name -- The name of the service to allow.
    response:
      { }  # Empty response on success

    """
    print args, kwargs
    self.allowService(uh, name)
    return {}
