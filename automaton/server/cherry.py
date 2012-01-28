import cherrypy
from cherrypy import tools
try:
  from simplejson import JSONEncoder
except ImportError:
  from json import JSONEncoder

from automaton.server.base import AutomatonServer
from automaton.lib import exceptions, logger


encoder = JSONEncoder()
def jsonify_tool_callback(*args, **kwargs):
    response = cherrypy.response
    response.headers['Content-Type'] = 'application/json'
    response.body = encoder.iterencode(response.body)
cherrypy.tools.jsonify = cherrypy.Tool('before_finalize',
  jsonify_tool_callback, priority=30)


class CherryServer(AutomatonServer):
  """Wrapper for building the AutomatonServer with CherryPy."""
  base_path = '/automaton'

  def __init__(self, withgui=False, port=9090):
    AutomatonServer.__init__(self, withgui)
    self.dispatch = cherrypy.dispatch.RoutesDispatcher()
    self.port = port

  def initialize(self):
    """Initialize CherryPy routes and exception handling."""
    self.dispatch.connect('register', '/register',
      controller=self, action='register_client')

    conf = {'/' : {'request.dispatch' : self.dispatch}}
    cherrypy.tree.mount(self, self.base_path, config=conf)
    
    cherrypy.config.update({
      'server.socket_host': '127.0.0.1',
      'server.socket_port': self.port,
      'request.error_response': self.handle_error
    })

  def _start(self):
    cherrypy.server.quickstart()
    cherrypy.engine.start()

  def handle_error(self):
    cherrypy.response.status = 500
    trace = cherrypy._cperror.format_exec()
    cherrypy.body = ["Error occurred:\n" + trace]
    logger.log(trace)

  @tools.jsonify()
  def register_client(self, appname=None, **kwargs):
    """Proxy for AutomatonServer's registerClient method.
    path: /register
    parameters:
      appname -- An identifier for the client. Prepended to a UID for
                  human-readable identification of clients.
    response:
      {
        "data": {
          "clientid": "my-app-4B82-A72D-2338"
        }
      }

    """
    clientid = self.registerClient(appname=appname)
    return {
      "data": {
        "clientid": clientid
      }
    }

  @tools.jsonify()
  def allow_service(self, clientid, name, *args, **kwargs):
    """Proxy for AutomatonServer's allowService method.
    path: /services/allow
    parameters:
      clientid -- The id identifying the client, returned from /register.
      name -- The name of the service to allow.
    response:
      { }  # Empty response on success

    """
    print args, kwargs
    self.allowService(clientid, name)
    return {}

"""
  void unregisterClient(1:string clientid) throws(1:ClientNotRegisteredError oops),

  void allowService(1:string clientid, 2:string name) throws (1:ClientNotRegisteredError oops, 2:ServiceNotProvidedError ouch),

  void disallowService(1:string clientid, 2:string name) throws (1:ClientNotRegisteredError oops, 2:ServiceNotRegisteredError ouch),

  void allowAllServices(1:string clientid) throws (1:ClientNotRegisteredError oops),

  void disallowAllServices(1:string clientid) throws (1:ClientNotRegisteredError oops),

  string interpret(1:string clientid, 2:string raw) throws(1:ClientNotRegisteredError oops, 2:ServiceNotRegisteredError ouch),

  bool isService(1:string name),

  set<string> getAvailableServices(),

  string serviceUsage(1:string name) throws (1:ClientNotRegisteredError oops, 2:ServiceNotProvidedError ouch)
"""
  

"""@get(base_path + '/services')
def __getAvailableServices():"""

if __name__ == "__main__":
  server = BottleServer()
  server.initialize()
  print 'Starting the server...'
  try:
    server.start()
  except KeyboardInterrupt:
    pass
