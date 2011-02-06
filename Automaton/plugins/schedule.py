import re
import os
import sys
import time
import pickle
import datetime
import threading
import Automaton.lib.utils as utils
import Automaton.lib.logger as logger
import Automaton.lib.platformdata as platformdata
import Automaton.lib.settings_loader as settings_loader
from Automaton.lib.PersistentQueue import PersistentPriorityQueue

if sys.version_info < (2, 7):
  raise Exception("Scheduler requires Python 2.7.")

class schedule:

  def remove_task_if_past(self):
    item = self.queue.front()
    if item[0] < datetime.datetime.now():
      return self.queue.get()
    else:
      return (item[0], None, None)

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
  
  def __init__(self):
    self.ops = {"QUEUE_FILE": None}
    self.ops.update(settings_loader.load_script_settings(__name__))

    if self.ops["QUEUE_FILE"] is None:
      self.ops["QUEUE_FILE"] = platformdata.getExistingFile("schedule.queue")
    else:
      if not os.access(self.ops["QUEUE_FILE"], os.W_OK):
        self.ops["QUEUE_FILE"] = None

    self.queue = PersistentPriorityQueue(storagefile=self.ops["QUEUE_FILE"])

    if self.ops["QUEUE_FILE"] is None:
      logger.log("Scheduler could not find an existing queue file and "
                 "no write access to create a new one. Any scheduled tasks "
                 "will disappear once server is stopped.")
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

    self.queue.put((t, match.group('cmd'), match.group('args')))
    self.event.set()
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
  # Used only for debugging. Overwritten by the AutomatonServer in "production".
  def call(self, cmd, arg):
    if cmd == "echo":
      return arg
    else:
      return "Please test with echo command."

if __name__=="__main__":
  __name__ = "schedule"
  s = schedule()
  print s.execute("echo done! in ten and a half seconds")
  time.sleep(3)
  print s.execute("echo first in one second")
  #print s.execute("echo absolute at 10:05pm")
  #s.execute("echo absolute at 5:00 A.M.")
  #s.execute("echo absolute at 5:00:4 AM")
  #s.execute("echo absolute at 5:55")
  time.sleep(60)
