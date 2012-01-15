import re
import os.path
import datetime
import threading

import autoplatform


class locked:  # pylint: disable-msg=C0103,R0903
  """Context manager for synchronizing blocks of code."""
  def __init__(self, lock):
    self.lock = lock

  def __enter__(self):
    self.lock.acquire()

  def __exit__(self, typ, value, traceback):
    self.lock.release()

def spawn_thread(func, *args):
  """Utility function for spawning a new thread by running the
  given function with the specified arguments.

  """
  thread = threading.Thread(target=func, args=args)
  thread.daemon = True
  thread.start()
  return thread

def get_module_name(fullname):
  """Pulls module name (eg. AIM) out of path (eg. /home/user/AIM.py)"""
  if fullname.endswith("py"):
    return os.path.splitext(os.path.basename(fullname))[0]
  else:
    return fullname[fullname.rfind('.') + 1:]

def get_app_settings_paths(name):
  name = get_module_name(name)
  return [os.path.join(base, "apps", name + ".conf") for base in
    autoplatform.get_dir_hierarchy()]

def get_plugin_settings_paths(name):
  name = get_module_name(name)
  return [os.path.join(base, "plugins", name + ".conf") for base in
    autoplatform.get_dir_hierarchy()]

# Adapted from:
# http://stackoverflow.com/questions/493174/
#   is-there-a-way-to-convert-number-words-to-integers-python
def text_to_int(textnum):
  """Convert numbers in word form to integers."""
  numwords = {}
  units = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen",
  ]

  tens = ["", "", "twenty", "thirty", "forty", "fifty",
          "sixty", "seventy", "eighty", "ninety"]

  modifiers = ["", "quarter", "half", "three-quarters"]

  numwords["and"] = 0
  for idx, word in enumerate(units):
    numwords[word] = idx
  for idx, word in enumerate(tens):
    numwords[word] = idx * 10
  for idx, word in enumerate(modifiers):
    numwords[word] = idx * .25

  current = result = 0
  for word in textnum.split():
    if word not in numwords:
      # We want to ignore modifiers...
      # Possibly want to ignore all unknowns?
      if word not in ("a",):
        raise Exception("Illegal word: " + word)
      else:
        continue

    increment = numwords[word]
    current = current + increment

  return result + current


# 5:34 pm
# 3:32:08 AM
# 5p.m. on Tuesday @TODO
# noon tomorrow @TODO
# 5pm every Monday ? @TODO
def text_to_absolute_time(text):
  """Convert an arbitrary time format into UNIX time."""
  match = re.search(r"""
    (?P<h>\d{1,2})            # Hour (required)
    (:(?P<m>\d{1,2}))?        # Optional Minutes
    (:(?P<s>\d{1,2}))?        # Optional Seconds
    (\s*(?P<tod>a|p)\.?m\.?)? # Optional am/p.m.
    """, text, flags=re.I | re.X)
  if match:
    hour = match.group('h')
    minute = match.group('m')
    sec = match.group('s')
    newtime = datetime.datetime.now()
    newtime.replace(microsecond=0)
    if match.group('tod'):
      if match.group('tod').lower() == 'a':
        newtime.replace(hour=int(hour))
      else:
        newtime.replace(hour=int(hour) + 12)
    # 24 hour or "closest next"?
    else:
      newtime.replace(hour=int(hour))
    if minute:
      newtime = newtime.replace(minute=int(minute))
    if sec:
      newtime = newtime.replace(second=int(sec))
    else:
      newtime = newtime.replace(second=0)
    if newtime < datetime.datetime.now():
      newtime += datetime.timedelta(days=1)
    return newtime

  else:
    return None
