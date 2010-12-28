import threading
import Queue
import datetime
import time
import re
import lib.logger as logger
import lib.utils as utils
import sys

if sys.version_info < (2, 7):
  raise Exception("Scheduler requires Python 2.7.")

class schedule:

  def _thread(self):
    while True:
      t, cmd, arg = self.queue.get()
      if t < datetime.datetime.now():
        try:
          val = self.call(cmd, arg)
        except Exception, e:
          val = "Exception encountered: %s" % e
        logger.log("Scheduled command %s has been run, with return value: \"%s\"" %
                    (cmd, val))
      else:
        self.queue.put((t, cmd, arg))
        twait = max((t-datetime.datetime.now()).total_seconds(),0)
        #print twait
        self.event.wait(twait)
        self.event.clear()

  # Used only for debugging. Overwritten by the AutomatonServer in "production".
  def call(self, cmd, arg):
    if cmd == "echo":
      return arg
    else:
      return "Please test with echo command."
  
  def __init__(self):
    #@TODO write to file instead of memory, in case of restart
    self.queue = Queue.PriorityQueue()
    self.event = threading.Event()
    thread = threading.Thread(target=self._thread)
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
