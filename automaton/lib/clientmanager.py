from collections import deque


class Client(object):

  def __init__(self, max_history):
    self.history = deque(maxlen=max_history)
    self.plugins = set()


class ClientManager(object):

  def __init__(self, max_history=20):
    self.max_history = max_history
    self.registeredclients = {}

  def add_client(self, ident):
    self.registeredclients[ident] = Client(self.max_history)
