import time
from threading import Lock
from collections import deque


class ResponseHistory(object):
  def __init__(self, response):
    self.response = response

  def __str__(self):
    return response

class QueryHistory(object):
  def __init__(self, raw, service, namespace, args):
    self.raw = raw
    self.service = service
    self.namespace = namespace
    self.args = args

  def __str__(self):
    return self.raw


class Client(object):  # pylint: disable-msg=R0903
  """Represents a connected client."""
  def __init__(self, max_history, name, uid):
    self.history = deque(maxlen=max_history)
    self.name = name
    self.uid = uid
    self.current_conversation = None
    self.last_contact = time.time()
    self.plugins = set()
    self.lock = Lock()

  def __str__(self):
    return "<Client {0}, last contacted: {1}".format(
      self.name, time.strftime("%d/%m/%Y %I:%M:%S%p"))


class PublishStream(object):
  """Represents an output stream that plugins can publish to."""
  def __init__(self, name, uid):
    self.name = name
    self.uid = uid


class ClientManager(object):  # pylint: disable-msg=R0903
  """Class to manage multiple connected clients."""
  def __init__(self, max_history=20):
    self.max_history = max_history
    self.registered_publishers = {}
    self.registered_clients = {}

  def add_client(self, ident, name=None):
    """Add a client to the list of registered clients."""
    self.registered_clients[ident] = Client(max_history=self.max_history,
    name=(name or ident), uid=ident)

  def add_publish_stream(self, ident, name=None):
    """Add a publish stream to the list of registered publishers."""
    self.registered_publishers[ident] = PublishStream(name=(name or ident),
                                                      uid=ident)

  def get_active_clients(self):
    return sorted(self.registered_clients.values(),
                    key=lambda client: client.last_contact, reversed=True)
