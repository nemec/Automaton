from threading import Lock
import copy

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
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self


    def fire(self, *args, **kargs):
        for handler in self.handlers:
            try:
              handler(*args, **kargs)
            except Exception as e:
              print e


    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount

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
        (structure defined in interpreter.py), and a lock that controls
        concurrent access to the service.

    """
    def __init__(self, svc, grammar = None, usage = ''):
      self.svc = svc
      self.grammar = grammar
      self.usage = usage
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
    self.services = {}
    self.__obj_lock = Lock()


  def register_service(self, svc_name, svc, grammar = None, usage = ''):
    self.services[svc_name.lower()] = self.__repo_svc(svc, grammar, usage)


  def remove_service(self, svc_name):
    svc_name = svc_name.lower()
    for name in self.services:
      service = self.services[name]
      if service.svc == svc:
        lock = service.lock
        lock.acquire()
        try:
          del self.services[name]
        finally:
          lock.release()


  def request_service(self, svc_name, *args, **kwargs):
    svc_name = svc_name.lower()
    if svc_name not in self.services:
      raise ServiceDoesNotExist("Service does not exist.")
    self.services[svc_name].lock.acquire()
    try:
      return self.services[svc_name].svc(*args, **kwargs)
    finally:
      self.services[svc_name].lock.release()


  def register_object(self, obj_name, obj):
    obj_name = obj_name.lower()
    self.__obj_lock.acquire()
    try:
      if obj_name not in self.objects:
        self.objects[obj_name] = self.__repo_obj(obj)
      else:
        self.objects[obj_name].obj = obj

      # Prevents the handler from needing a call to get_object
      self.objects[obj_name].change_event.fire(obj)

    finally:
      self.__obj_lock.release()


  def remove_object(self, obj_name):
    obj_name = obj_name.lower()
    self.__obj_lock.acquire()
    try:
      del self.objects[obj_name]
    finally:
      self.__obj_lock.release()


  def register_object_listener(self, obj_name, callback):
    obj_name = obj_name.lower()
    if obj_name not in self.objects:
      self.objects[obj_name] = (None, Event())

    self.objects[obj_name].change_event += callback


  def remove_object_listener(self, obj_name, callback):
    obj_name = obj_name.lower()
    if obj_name in self.objects:
      self.objects[obj_name].change_event -= callback


  def get_object(self, obj_name):
    """ get_object returns a shallow copy of the object in the repository """

    obj_name = obj_name.lower()
    if obj_name not in self.objects or self.objects[obj_name] is None:
      raise ObjectDoesNotExist(obj_name)
    return copy.copy(self.objects[obj_name].obj)


if __name__ == "__main__":
  class C(object):
    def __init__(self):
      self.x = 4

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

  def service(name):
    print "Hello, {0}.".format(name)

  r.register_service("name", service)
  r.request_service("name", "tim")
