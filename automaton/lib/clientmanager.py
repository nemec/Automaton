import time
from threading import Lock
from collections import deque


class Client(object):  # pylint: disable-msg=R0903
  """Represents a connected client."""
  def __init__(self, max_history):
    self.history = deque(maxlen=max_history)
    self.current_conversation = None
    self.last_contact = time.time()
    self.plugins = set()
    self.lock = Lock()


class ClientManager(object):  # pylint: disable-msg=R0903
  """Class to manage multiple connected clients."""
  def __init__(self, max_history=20):
    self.max_history = max_history
    self.registered_clients = {}

  def add_client(self, ident):
    """Add a client to the list of registered clients."""
    self.registered_clients[ident] = Client(self.max_history)
