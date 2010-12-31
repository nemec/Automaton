import re
import os
import sys
import time
import Queue
import pickle
import datetime
import threading
import lib.utils as utils
import lib.logger as logger
import lib.platformdata as platformdata
import lib.settings_loader as settings_loader

if sys.version_info < (2, 7):
  raise Exception("Scheduler requires Python 2.7.")

class schedule:

  def add_task(self, task):
    self.queue_lock.acquire()
    try:
      self.queue.put(task)
      try:
        if self.ops["QUEUE_FILE"] is not None:
          f = open(self.ops["QUEUE_FILE"], 'w')
          pickle.dump(self.queue.queue, f)
          f.close()
      except IOError, e:
        if e.args[0] == 13:
          logger.log("No access to scheduler file. Could not store current"
                     "queue data.")
      self.event.set()
    finally:
      self.queue_lock.release()

  def remove_task_if_past(self):
    item = self.queue.get()
    self.queue_lock.acquire()
    try:
      if item[0] < datetime.datetime.now():
        try:
          if self.ops["QUEUE_FILE"] is not None:
            f = open(self.ops["QUEUE_FILE"], 'w')
            pickle.dump(self.queue.queue, f)
            f.close()
        except IOError, e:
          if e.args[0] == 13:
            logger.log("No access to scheduler file. Could not store current"
                       "queue data.")
        return item
      else:
        self.queue.put(item)
        return (item[0], None, None)
    finally:
      self.queue_lock.release()

  def _executionthread(self):
    while True:
      t, cmd, arg = self.remove_task_if_past()
      if cmd is not None:
        try:
          val = self.call(cmd, arg)
        except Exception, e:
          val = "Exception encountered: %s" % e
        logger.log("Scheduled command %s has been run, with return value: \"%s\"" %
                    (cmd, val))
      else:
        twait = max((t-datetime.datetime.now()).total_seconds(),0)
        self.event.wait(twait)
        self.event.clear()

  # Used only for debugging. Overwritten by the AutomatonServer in "production".
  def call(self, cmd, arg):
    if cmd == "echo":
      return arg
    else:
      return "Please test with echo command."
  
  def __init__(self):
    self.queue = Queue.PriorityQueue()
    self.ops = {"QUEUE_FILE": None}
    self.ops.update(settings_loader.load_script_settings(__name__))
    if self.ops["QUEUE_FILE"] is None:
      for d in platformdata.getDirHierarchy():
        if os.path.exists(d):
          filepath = os.path.join(scriptpath,scriptname)
          if os.access(filepath, os.W_OK):
            self.ops["QUEUE_FILE"] = filepath
            break
    else:
      try:
        if os.access(self.ops["QUEUE_FILE"], os.W_OK):
          if os.path.exists(self.ops["QUEUE_FILE"]):
            f = open(self.ops["QUEUE_FILE"], 'r')
            self.queue.queue = pickle.load(f)
            f.close()
        else:
          self.ops["QUEUE_FILE"] = None
      except Exception, e:
        print e
        pass
    if self.ops["QUEUE_FILE"] is None:
      logger.log("Scheduler could not find an existing queue file and "
                 "no write access to create a new one. Any scheduled tasks "
                 "will disappear once server is stopped.")
    self.queue_lock = threading.Lock()
    self.event = threading.Event()
    thread = threading.Thread(target=self._executionthread)
    thread.setDaemon(True)
    thread.start()
  
  def execute(self, arg = ''):
    t = 0
    # Matches either "cmd arg in x seconds" or "cmd arg at time"
    match = re.match(r"(?P<cmd>.*?) "+
                     r"(?P<args>.*?)\s*"+
                     r"((?P<in>in)|(?P<at>at))\s*"+
                     r"(?P<time>.*)"+
                     r"(?(in)(?P<tscale>hour|minute|second)s?)", arg, flags=re.I)
    if match:
      # Relative time
      if match.group('in'):
        try:
          t = int(match.group('time'))
        except ValueError:
          try:
            t = utils.text_to_int(match.group('time'))
          except:
            return "Error parsing time."
        scale = match.group('tscale')
        if scale == "hour":
          t = datetime.datetime.now() + datetime.timedelta(hours = t)
        elif scale == "minute":
          t = datetime.datetime.now() + datetime.timedelta(minutes = t)
        elif scale == "second":
          t = datetime.datetime.now() + datetime.timedelta(seconds = t)
        else:
          return "Could not determing time scale (h/m/s)."
      # Absolute time
      else:
        t = utils.text_to_absolute_time(match.group('time'))
        if not t:
          return "Error parsing time."
    else:
      return 'Command could not be scheduled.'

    self.add_task((t, match.group('cmd'), match.group('args')))
    return 'Command scheduled.'

  def grammar(self):
    return  "schedule{"+\
              "keywords = schedule"+\
              "arguments = *"+\
            "}"

  def platform(self):
    return ['linux', 'windows', 'mac']

  def help(self):
    return """
            USAGE: schedule WHAT [at WHEN] | [in WHEN]
            Schedules a command to be run at a specific time, repeating if
            necessary.
           """

if __name__=="__main__":
  __name__ = "schedule"
  s = schedule()
  print s.execute("echo done! in ten and a half seconds")
  time.sleep(3)
  print s.execute("echo first in one second")
  print s.execute("echo absolute at 10:05pm")
  #s.execute("echo absolute at 5:00 A.M.")
  #s.execute("echo absolute at 5:00:4 AM")
  #s.execute("echo absolute at 5:55")
  time.sleep(60)
