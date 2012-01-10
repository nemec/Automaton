import copy
from threading import Lock
from collections import defaultdict

from automaton.lib.interpreter import Interpreter
from automaton.lib.utils import locked
import automaton.lib.logger as logger


class ServiceDoesNotExist(Exception):
  """Indicates that a requested service
  does not exist in the registrar.

  """
  pass


class ObjectDoesNotExist(Exception):
  """Indicates that a specified object
  does not exist in the registrar.

  """
  pass


def _copy(obj):
  """Create a shallow copy of an object. Provides shortcuts for
  certain object types with known copy features, using copy.copy for
  everything else.

  """
  typ = type(obj)
  if typ is list:
    return list(obj)
  elif typ is dict:
    return dict(obj)
  else:
    return copy.copy(obj)


class Event:
  """ Event Handler
      Code for event handler management taken from:
      http://www.valuedlessons.com/2008/04/events-in-python.html

  """

  def __init__(self):
    self.handlers = set()

  def handle(self, handler):
    """Register the callable to be executed by this event."""
    self.handlers.add(handler)
    return self

  def unhandle(self, handler):
    """Remove the specified callable from being handled by this event."""
    try:
      self.handlers.remove(handler)
    except:
      raise ValueError("Handler is not handling this event, "
                          "so cannot unhandle it.")
    return self

  def fire(self, *args, **kargs):
    """Execute all callables registered to this event."""
    for handler in self.handlers:
      try:
        handler(*args, **kargs)
      except Exception as err:  # pylint: disable-msg=W0703
        # We don't want a rogue handler to mess up everyone else
        logger.log("Exception encountered during event handling", err)

  __iadd__ = handle
  __isub__ = unhandle
  __call__ = fire
  __len__ = lambda self: len(self.handlers)


class Registrar(object):
  """
    The Registrar defines a collection where services and objects can
    be registered. Other classes can then use and listen for those
    services and objects.

  """

  class _RepoSvc(object):  # pylint: disable-msg=R0903
    """ Repository Service
        Consists of the service function, a grammar that defines how
        a POS tagged query is to be turned into the service's arguments
        (structure defined in interpreter.py), a lock that controls
        concurrent access to the service, and an optional namespace to
        prevent plugins offering similar/same services from stepping on
        each others' toes.

    """
    def __init__(self, name, svc, grammar=None, usage='', namespace=None):
      self.name = name
      self.svc = svc
      self.grammar = grammar
      self.usage = usage
      self.namespace = namespace
      self.lock = Lock()

  class _RepoObj(object):  # pylint: disable-msg=R0903
    """ Repository Object
        Consists of an object placed into the repository and an event
        that handles alerting interested parties of changes to the object.
        The object itself should only change upon calls to register_object().
        Any changes to complex types may not produce a change_event signal.

    """
    def __init__(self, obj):
      self.obj = obj
      self.change_event = Event()

  def __init__(self):
    self.objects = {}
    self.services = defaultdict(dict)
    self.__obj_lock = Lock()
    self.interpreter = Interpreter(self)

  def find_best_service(self, query):
    """Use the interpreter to find the single best
    (service, namespace, arguments) triplet for the given query.

    """
    return self.interpreter.best_interpretation(query)

  def find_services(self, query):
    """Use the interpreter to turn the query into a list of
    (service, namespace, arguments) triplets.

    """
    return self.interpreter.interpret(query)

  def register_service(self, svc_name, svc_func,
      grammar=None, usage='', namespace=None):
    """Register a function to be made available to clients and plugins.
    
    Keyword arguments:
    svc_name -- the name the service is registered under (may be a duplicate
      of an existing service)
    svc_func -- the function called when the service is requested
    grammar -- the grammar (defined in the Interpreter) that describes how
      keyword arguments for svc_func are assembled (default None)
    usage -- a string quickly defining how to use the service. Any
      occurrance of '%s' in the usage will be replaced with the name
      of the service. (default '')
    namespace -- any hashable object (preferably a string). When combined
      with svc_name, it is used to uniquely identify a specific implementation
      of a service. If both the svc_name and namespace collide, the service is
      overwritten. (default None)

    """
    usage = usage.replace('%s', svc_name)
    self.services[svc_name.lower()][namespace] = self._RepoSvc(
        name=svc_name.lower(), svc=svc_func, grammar=grammar,
        usage=usage, namespace=namespace)

  def unregister_service(self, svc_name, namespace=None):
    """Remove the registered service with the provided name and
    (optional) namespace.

    """
    svc_name = svc_name.lower()
    if (svc_name in self.services and
        namespace in self.services[svc_name]):
      with locked(self.services[svc_name][namespace].lock):
        if len(self.services[svc_name]) == 1:
          del self.services[svc_name]  # last service by this name
        else:  # remove the service namespace
          del self.services[svc_name][namespace]

  def request_service(self, svc_name, namespace=None, argdict=None, **kwargs):
    """Call the service registered to svc_name with the specified (optional)
    namespace and given kwargs.

    """
    svc_name = svc_name.lower()
    if (svc_name not in self.services or
        namespace not in self.services[svc_name]):
      raise ServiceDoesNotExist("Service does not exist.")
    with locked(self.services[svc_name][namespace].lock):
      if argdict:
        try:
          kwargs.update(argdict)
        except AttributeError:
          pass
      return self.services[svc_name][namespace].svc(**kwargs)

  def register_object(self, obj_name, obj):
    """Create a shallow copy of the provided object and register it.
    WARNING: Anything beyond simple objects may be changed without warning
    by other plugins.

    """
    obj_name = obj_name.lower()
    with locked(self.__obj_lock):
      if obj_name not in self.objects:
        self.objects[obj_name] = self._RepoObj(_copy(obj))
      else:
        self.objects[obj_name].obj = obj

      # Prevents the handler from needing a call to get_object
      self.objects[obj_name].change_event.fire(obj)

  def remove_object(self, obj_name):
    """Remove a registered object from the internal cache."""
    obj_name = obj_name.lower()
    with locked(self.__obj_lock):
      del self.objects[obj_name]

  def register_object_listener(self, obj_name, callback):
    """Register a callback to be executed whenever an object with the
    specified name is registered.
    
    Callback should take one argument - the new object

    """
    obj_name = obj_name.lower()
    if obj_name not in self.objects:
      self.objects[obj_name] = self._RepoObj(None)

    self.objects[obj_name].change_event += callback

  def remove_object_listener(self, obj_name, callback):
    """Remove the given callback from being run when the object registered
    under obj_name is updated. Must be called with the same function the
    listener was registered with.

    """
    obj_name = obj_name.lower()
    if obj_name in self.objects:
      self.objects[obj_name].change_event -= callback

  def get_object(self, obj_name):
    """Return a shallow copy of the object in the repository.
    WARNING: Anything beyond simple objects may be changed without warning
    by other plugins.

    """
    obj_name = obj_name.lower()
    if obj_name not in self.objects or self.objects[obj_name] is None:
      raise ObjectDoesNotExist(obj_name)
    return _copy(self.objects[obj_name].obj)

#TODO turn into unit test
"""if __name__ == "__main__":
  class D(object):
    def __init__(self, i=4):
      self.c = i

  class C(object):
    def __init__(self):
      self.x = D()

  c = C()

  r = Registrar()
  r.register_object("o", c)

  a = r.get_object("o")
  b = r.get_object("o")
  a.x = 3
  print b.x == 4

  def func(obj):
    print "hello", obj

  def func_a(obj):
    print "should print only once"

  r.register_object_listener("o", func)
  r.register_object_listener("o", func_a)
  r.register_object("o", 6)

  r.remove_object_listener("o", func_a)
  r.register_object("o", 8)

  def service(**kwargs):
    print "Hello, {0}.".format(kwargs["name"])

  r.register_service("name", service)
  r.request_service("name", name="tim")"""
