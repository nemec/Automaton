import threading
import Queue
from time import time as curtime
from time import sleep
import re
import lib.logger as logger

class schedule:

  # Adapted from http://stackoverflow.com/questions/493174/is-there-a-way-to-convert-number-words-to-integers-python
  def text2int(self, textnum):
    numwords = {}
    units = [
      "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
      "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
      "sixteen", "seventeen", "eighteen", "nineteen",
    ]

    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

    modifiers = ["", "quarter", "half", "three-quarters"]

    numwords["and"] = 0
    for idx, word in enumerate(units):      numwords[word] = idx
    for idx, word in enumerate(tens):       numwords[word] = idx * 10
    for idx, word in enumerate(modifiers):  numwords[word] = idx * .25

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          # We want to ignore modifiers...
          # Possibly want to ignore all unknowns?
          if word not in ("a", ): 
            raise Exception("Illegal word: " + word)
          else:
            continue

        increment = numwords[word]
        current = current  + increment

    return result + current

  def _thread(self):
    while True:
      time, cmd, arg = self.queue.get()
      if time < curtime():
        logger.log("Scheduled command has been run, with return value: \"" +
                    self.call(cmd, arg) + "\"")
      else:
        self.queue.put((time, cmd, arg))
        sleep(max(time-curtime(),0))

  def call(self, cmd, arg):
    if cmd == "echo":
      return arg
    else:
      return "Please test with echo command."
  
  def __init__(self):
    #@TODO write to file instead of memory, in case of restart
    self.queue = Queue.PriorityQueue()
    thread = threading.Thread(target=self._thread)
    thread.setDaemon(True)
    thread.start()
  
  def execute(self, arg = ''):
    time = 0
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
          time = int(match.group('time'))
        except ValueError:
          try:
            time = self.text2int(match.group('time'))
          except:
            return "Error parsing time."
        scale = match.group('tscale')
        if scale == "hour":
          time = curtime() + time * 3600
        elif scale == "minute":
          time = curtime() + time * 60
        elif scale == "second":
          time = curtime() + time
        else:
          return "Could not determing time scale (h/m/s)."
      # Absolute time
      else:
        return "Absolute time not yet implemented."
        #print match.group('time')
    else:
      return 'Command could not be scheduled.'
    self.queue.put((time, match.group('cmd'), match.group('args')))
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
  print s.execute("echo done! in three and a half seconds")
  print s.execute("echo done! at 5 pm")
  sleep(5)
