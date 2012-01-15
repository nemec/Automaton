import os
import sys
import datetime
import threading
import ConfigParser

from automaton.lib import utils, plugin, logger, autoplatform
from automaton.lib.persistent_queue import PersistentPriorityQueue

if sys.version_info < (2, 7):
  raise Exception("Scheduler requires Python 2.7.")


def platform():
  """Return the list of platforms the plugin is available for."""
  return ['linux', 'windows', 'mac']


class Schedule(plugin.PluginInterface):
  """Plugin for scheduling other tasks to be run later."""
  def remove_task_if_past(self):
    """Remove the task from the queue if the expiration time is past."""
    item = self.queue.front()
    if item[0] < datetime.datetime.now():
      return self.queue.get()
    else:
      return (item[0], (None, None, None))

  def _executionthread(self):
    """Continually poll the queue for tasks to be run."""
    while True:
      expire, (command, namespace, args) = self.remove_task_if_past()
      if command is not None:
        val = None
        try:
          val = self.registrar.request_service(
            command, namespace=namespace, argdict=args)
        except Exception as err:
          val = "Exception encountered: {0}".format(err)
        logger.log("Scheduled command {0} has been run, with "
                   "return value: \"{1}\"".format(command, val))
      else:
        twait = max((expire - datetime.datetime.now()).total_seconds(), 0)
        self.event.wait(twait)
        self.event.clear()

  def __init__(self, registrar):
    super(Schedule, self).__init__(registrar)
    self.settings = ConfigParser.SafeConfigParser()
    self.settings.read(utils.get_plugin_settings_paths(__name__))

    if not self.settings.has_option("Settings", "queue_file"):
      self.settings.set("Settings", "queue_file",
        autoplatform.get_existing_file("schedule.queue"))
    else:
      if not os.access(self.settings.get("Settings", "queue_file"), os.W_OK):
        self.settings.set("Settings", "queue_file", None)

    self.queue = PersistentPriorityQueue(
      storagefile=self.settings.get("Settings", "queue_file"))

    if not self.settings.has_option("Settings", "queue_file") or
      self.settings.get("Settings", "queue_file") is None:
      logger.log("Scheduler could not find an existing queue file and "
                 "no write access to create a new one. Any scheduled tasks "
                 "will disappear once server is stopped.")

    self.event = threading.Event()
    thread = threading.Thread(target=self._executionthread)
    thread.setDaemon(True)
    thread.start()

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
    """Disable all of Schedule's services."""
    self.registrar.unregister_service("schedule", namespace=__name__)

  def execute(self, **kwargs):
    """Schedule a command to be run at a later time.

    Keyword arguments:
    command -- the command (in natural language) to be run
    in -- a relative time offset (hours, minutes, and/or seconds)
    at -- an absolute time to run the command

    """
    expire = 0
    if "command" not in kwargs:
      raise plugin.UnsuccessfulExecution("No command provided.")
    
    if "in" in kwargs:
      try:
        idx = kwargs["in"].rfind(" ")
        wait = kwargs["in"][:idx]
        scale = kwargs["in"][idx + 1:]
      except ValueError:
        raise plugin.UnsuccessfulExecution("Error parsing time.")
      try:
        expire = int(wait)
      except ValueError:
        try:
          expire = utils.text_to_int(wait)
        except:
          raise plugin.UnsuccessfulExecution("Error parsing time.")
      if scale.startswith("h"):
        expire = datetime.datetime.now() + datetime.timedelta(hours=expire)
      elif scale.startswith("m"):
        expire = datetime.datetime.now() + datetime.timedelta(minutes=expire)
      elif scale.startswith("s"):
        expire = datetime.datetime.now() + datetime.timedelta(seconds=expire)
      else:
        raise plugin.UnsuccessfulExecution(
                          "Could not determine time scale (h/m/s).")
    elif "at" in kwargs:
      expire = utils.text_to_absolute_time(wait)
      if not expire:
        raise plugin.UnsuccessfulExecution("Error parsing time.")        
    else:
      raise plugin.UnsuccessfulExecution(
        'Command could not be scheduled. Must specify "in" or "at"')

    cmd, namespace, args = self.registrar.find_best_service(kwargs["command"])
    if cmd is None:
      raise plugin.UnsuccessfulExecution("Provided text could not be "
        "converted into a command.")
    self.queue.put((expire, (cmd, namespace, args)))
    self.event.set()
    return 'Command scheduled.'

#TODO Move to a unit test
"""if __name__ == "__main__":
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
  time.sleep(60)"""
