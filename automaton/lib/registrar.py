import copy
from threading import Lock
from collections import defaultdict

from interpreter import Interpreter
from utils import locked


class ServiceDoesNotExist(Exception):
  pass


class ObjectDoesNotExist(Exception):
  pass


class Event:
    """ Event Handler
        Code for event handler management taken from:
        http://www.valuedlessons.com/2008/04/events-in-python.html

    """

    def __init__(self):
        self.handlers = set()

    def handle(self, handler):
        self.handlers.add(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, "
                              "so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            try:
              handler(*args, **kargs)
            except Exception as e:
              # We don't want a rogue handler to mess up everyone else
              print e

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__ = getHandlerCount


class Registrar(object):
  """
    The Registrar defines a collection where services and objects can
    be registered. Other classes can then use and listen for those
    services and objects.

  """

  class __repo_svc(object):
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
      self.namespace = None
      self.lock = Lock()

  class __repo_obj(object):
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
    return self.interpreter.best_interpretation(query)

  def find_services(self, query):
    return self.interpreter.interpret(query)

  def register_service(self, svc_name, svc_func,
      grammar=None, usage='', namespace=None):
    self.services[svc_name.lower()][namespace] = self.__repo_svc(
        name=svc_name.lower(), svc=svc_func, grammar=grammar,
        usage=usage, namespace=namespace)

  def remove_service(self, svc_name, namespace=None):
    svc_name = svc_name.lower()
    if (svc_name in self.services and
        namespace in self.services[svc_name]):
      with locked(self.services[svc_name][namespace].lock):
        if len(self.services[svc_name]) == 1:
          del self.services[svc_name]  # last service by this name
        else:  # remove the service namespace
          del self.services[svc_name][namespace]

  def request_service(self, svc_name, namespace=None, *args, **kwargs):
    svc_name = svc_name.lower()
    if (svc_name not in self.services or
        namespace not in self.services[svc_name]):
      raise ServiceDoesNotExist("Service does not exist.")
    with locked(self.services[svc_name][namespace].lock):
      return self.services[svc_name][namespace].svc(*args, **kwargs)

  def register_object(self, obj_name, obj):
    """ Register Object
        Creates a deep copy of the provided object to prevent changes
        then inserts it into the object dictionary
    """
    obj_name = obj_name.lower()
    with locked(self.__obj_lock):
      if obj_name not in self.objects:
        self.objects[obj_name] = self.__repo_obj(copy.deepcopy(obj))
      else:
        self.objects[obj_name].obj = obj

      # Prevents the handler from needing a call to get_object
      self.objects[obj_name].change_event.fire(obj)

  def remove_object(self, obj_name):
    obj_name = obj_name.lower()
    with locked(self.__obj_lock):
      del self.objects[obj_name]

  def register_object_listener(self, obj_name, callback):
    obj_name = obj_name.lower()
    if obj_name not in self.objects:
      self.objects[obj_name] = self.__repo_obj(None)

    self.objects[obj_name].change_event += callback

  def remove_object_listener(self, obj_name, callback):
    obj_name = obj_name.lower()
    if obj_name in self.objects:
      self.objects[obj_name].change_event -= callback

  def get_object(self, obj_name):
    """ get_object returns a deep copy of the object in the repository """

    obj_name = obj_name.lower()
    if obj_name not in self.objects or self.objects[obj_name] is None:
      raise ObjectDoesNotExist(obj_name)
    return copy.deepcopy(self.objects[obj_name].obj)


if __name__ == "__main__":
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
  r.request_service("name", name="tim")
