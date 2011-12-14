import re
import os
import sys
import time
import pickle
import datetime
import threading

import automaton.lib.utils as utils
import automaton.lib.plugin as plugin
import automaton.lib.logger as logger
import automaton.lib.interpreter as interpreter
import automaton.lib.autoplatform as autoplatform
import automaton.lib.settings_loader as settings_loader
from automaton.lib.persistent_queue import PersistentPriorityQueue

if sys.version_info < (2, 7):
  raise Exception("Scheduler requires Python 2.7.")


def platform():
  return ['linux', 'windows', 'mac']


class Schedule(plugin.PluginInterface):

  def remove_task_if_past(self):
    item = self.queue.front()
    if item[0] < datetime.datetime.now():
      return self.queue.get()
    else:
      return (item[0], (None, None, None))

  def _executionthread(self):
    while True:
      t, (command, namespace, args) = self.remove_task_if_past()
      if command is not None:
        val = None
        try:
          val = self.registrar.request_service(
            command, namespace=namespace, **args)
        except Exception as e:
          val = "Exception encountered: {0}".format(e)
        logger.log("Scheduled command {0} has been run, with "
                   "return value: \"{1}\"".format(command, val))
      else:
        twait = max((t - datetime.datetime.now()).total_seconds(), 0)
        self.event.wait(twait)
        self.event.clear()

  def __init__(self, registrar):
    super(Schedule, self).__init__(registrar)
    self.ops = {"QUEUE_FILE": None}
    self.ops.update(settings_loader.load_plugin_settings(__name__))

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

    self.registrar = registrar
    self.registrar.register_service("schedule", self.execute,
      grammar={
        "at": ["at"],
        "in": ["in"],
        "command": [],
      },
      usage=("USAGE: schedule WHAT [at WHEN] | [in WHEN]\n"
            "Schedules a command to be run at a specific time, repeating if\n"
            "necessary."),
      namespace=__name__)

  def disable(self):
    self.registrar.unregister_service("schedule", namespace=__name__)

  def execute(self, **kwargs):
    t = 0
    if "command" not in kwargs:
      raise plugin.UnsuccessfulExecution("No command provided.")
    
    if "in" in kwargs:
      try:
        ix = kwargs["in"].rfind(" ")
        time = kwargs["in"][:ix]
        scale = kwargs["in"][ix + 1:]
      except ValueError:
        raise plugin.UnsuccessfulExecution("Error parsing time.")
      try:
        t = int(time)
      except ValueError:
        try:
          t = utils.text_to_int(time)
        except:
          raise plugin.UnsuccessfulExecution("Error parsing time.")
      if scale.startswith("h"):
        t = datetime.datetime.now() + datetime.timedelta(hours=t)
      elif scale.startswith("m"):
        t = datetime.datetime.now() + datetime.timedelta(minutes=t)
      elif scale.startswith("s"):
        t = datetime.datetime.now() + datetime.timedelta(seconds=t)
      else:
        raise plugin.UnsuccessfulExecution(
                          "Could not determine time scale (h/m/s).")
    elif "at" in kwargs:
      t = utils.text_to_absolute_time(match.group('time'))
      if not t:
        raise plugin.UnsuccessfulExecution("Error parsing time.")        
    else:
      raise plugin.UnsuccessfulExecution('Command could not be scheduled. Must specify "in" or "at"')

    cmd, namespace, args = self.registrar.find_best_service(kwargs["command"])
    if cmd is None:
      raise plugin.UnsuccessfulExecution("Provided text could not be "
        "converted into a command.")
    self.queue.put((t, (cmd, namespace, args)))
    self.event.set()
    return 'Command scheduled.'


if __name__ == "__main__":
  __name__ = "schedule"
  import automaton.lib.registrar as registrar
  r = registrar.Registrar()
  def echo(**kwargs):
    return kwargs["command"]
  r.register_service("echo", echo, {"command":[]})
  
  s = Schedule(r)
  args = {"command": "echo done!", "in": "ten and a half seconds"}
  print s.execute(**args)
  time.sleep(3)
  
  args = {"command": "echo first", "in": "one second"}
  print s.execute(**args)
  #print s.execute("echo absolute at 10:05pm")
  #s.execute("echo absolute at 5:00 A.M.")
  #s.execute("echo absolute at 5:00:4 AM")
  #s.execute("echo absolute at 5:55")
  time.sleep(60)
