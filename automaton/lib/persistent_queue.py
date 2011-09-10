import Queue
import pickle

# ATTENTION: This writes the entire list every time something is added or
# removed. Thus, it is very very very slow for large lists.
# Currently, optimization seems to be unnecessary so it will not be
# implemented. If you are interested in scalable object persistence, check
# out http://www.zodb.org/


class PersistentPriorityQueue(Queue.PriorityQueue):
  # Pickles queue to file on get/put
  # Since it doesn't read the file again once it's been
  # loaded, queue files can't be shared between objects

  def __init__(self, maxsize=0, storagefile=None):
    self.file = storagefile
    Queue.PriorityQueue.__init__(self, maxsize)

  def _init(self, maxsize):
    self.__load()

  def _put(self, item):
    Queue.PriorityQueue._put(self, item)
    if self.file is not None:
      self.__dump()

  def _get(self):
    item = Queue.PriorityQueue._get(self)
    if self.file is not None:
      self.__dump()
    return item

  def __load(self):
    try:
      f = open(self.file, 'r')
      self.queue = pickle.load(f)
      f.close()
    except:
      self.queue = []

  def __dump(self):
    f = open(self.file, 'w')
    pickle.dump(self.queue, f)
    f.close()

  def front(self, block=True, timeout=None):
    self.not_empty.acquire()
    try:
      if not block:
        if not self._qsize():
          raise Empty
      elif timeout is None:
        while not self._qsize():
          self.not_empty.wait()
      elif timeout < 0:
        raise ValueError("'timeout' must be a positive number")
      else:
        endtime = _time() + timeout
        while not self._qsize():
          remaining = endtime - _time()
          if remaining <= 0.0:
            raise Empty
          self.not_empty.wait(remaining)
      item = self.queue[0]
      self.not_full.notify()
      return item
    finally:
      self.not_empty.release()

  def front_nowait(self):
    self.not_empty.acquire()
    try:
      if not self._qsize():
        return Queue.Empty()
      return self.queue[0]
    finally:
      self.not_empty.release()

if __name__ == "__main__":
  q = PersistentPriorityQueue(storagefile="file")
  q.put(5)
  q.put(3)
  q.put(4)
  print q.get()
  print q.front()
  print q.get()

  # Emulates closing/reopening the queue
  q = PersistentPriorityQueue(storagefile="file")
  print q.get()
