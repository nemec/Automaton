import time
import heapq
import Queue
import pickle


class PersistentPriorityQueue(Queue.PriorityQueue):
  """
  Pickles queue to file on get/put.
  Since it doesn't read the file again once it's been
  loaded, queue files can't be shared between objects.
  
  ATTENTION: This writes the entire list every time something is added or
  removed. Thus, it is very very very slow for large lists.
  Currently, optimization seems to be unnecessary so it will not be
  implemented. If you are interested in scalable object persistence, check
  out http://www.zodb.org/

  """

  def __init__(self, maxsize=0, storagefile=None):
    Queue.PriorityQueue.__init__(self, maxsize)
    self.file = storagefile

  def _init(self, maxsize):
    self.queue = []
    self.__load()

  def _put(self, item, heappush=heapq.heappush):
    Queue.PriorityQueue._put(self, item, block, timeout)
    if self.file is not None:
      self.__dump()

  def _get(self, heappush=heapq.heappush):
    item = Queue.PriorityQueue._get(self)
    if self.file is not None:
      self.__dump()
    return item

  def __load(self):
    """Load queue from pickled file."""
    try:
      with open(self.file, 'r') as fil:
        self.queue = pickle.load(fil)
    except IOError:
      pass

  def __dump(self):
    """Dump queue to pickled file."""
    with open(self.file, 'w') as fil:
      pickle.dump(self.queue, fil)

  def front(self, block=True, timeout=None):
    """Peek at the front of the queue, blocking if necessary."""
    self.not_empty.acquire()
    try:
      if not block:
        if not self._qsize():
          raise Queue.Empty
      elif timeout is None:
        while not self._qsize():
          self.not_empty.wait()
      elif timeout < 0:
        raise ValueError("'timeout' must be a positive number")
      else:
        endtime = time.time() + timeout
        while not self._qsize():
          remaining = endtime - time.time()
          if remaining <= 0.0:
            raise Queue.Empty
          self.not_empty.wait(remaining)
      item = self.queue[0]
      self.not_full.notify()
      return item
    finally:
      self.not_empty.release()

  def front_nowait(self):
    """Peek at the front of the queue."""
    self.not_empty.acquire()
    try:
      if not self._qsize():
        raise Queue.Empty
      return self.queue[0]
    finally:
      self.not_empty.release()

#TODO Move to unit test
"""if __name__ == "__main__":
  q = PersistentPriorityQueue(storagefile="file")
  q.put(5)
  q.put(3)
  q.put(4)
  print q.get()
  print q.front()
  print q.get()

  # Emulates closing/reopening the queue
  q = PersistentPriorityQueue(storagefile="file")
  print q.get()"""
