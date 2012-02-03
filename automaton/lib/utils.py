import re
import os.path
import datetime
import threading

from automaton.lib import autoplatform


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
  """Pull module name (eg. AIM) out of path (eg. /home/user/AIM.py)"""
  basename = os.path.basename(fullname)
  if basename.endswith("py"):
    return os.path.splitext(basename)[0]
  else:
    return basename[basename.rfind('.') + 1:]


def get_app_settings_paths(name):
  """Return an ordered list of possible settings filepaths for apps."""
  name = get_module_name(name)
  return [os.path.join(base, "apps", name + ".conf") for base in
    autoplatform.get_dir_hierarchy()]


def get_plugin_settings_paths(name):
  """Return an ordered list of possible settings filepaths for plugins."""
  name = get_module_name(name)
  return [os.path.join(base, "plugins", name + ".conf") for base in
    autoplatform.get_dir_hierarchy()]


def humanize_join(sequence, separator=',', spacing=' ',
                  conjunction='or', oxford_comma=True):
  """
  Join a list together using the English syntax of inserting a
  conjunction before the last item.
  
  Keyword Arguments:
    sequence -- The sequence to join together. Convert iterables to sequences
      using list() if necessary.
    separator -- The string to separate each item with.
    spacing -- A string appended to the separator to space out sequence
                members (such as a space in sentences).
    conjunction -- A string to insert between the last separator and the
      final item in the sequence.
    oxford_comma -- Boolean value that indicates whether or not to include
      the separator before the conjunction inserted before the last item
      in the sequence. Since there is no consensus on whether or not to use
      the Oxford comma, it is provided as an option.

  """
  lst = list(sequence)
  full_sep = separator + spacing
  string = full_sep.join(lst)
  if len(lst) > 1:
    last = lst[-1]
    if not oxford_comma or len(lst) == 2:
      start = string[:-len(last)-len(full_sep)]  # Remove the last comma
    else:
      start = string[:-len(last) - len(spacing)]
    return ''.join([start, spacing, conjunction, spacing, string[-len(last):]])
  else:
    return string

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
  numwords["a"] = 0
  for idx, word in enumerate(units):
    numwords[word] = idx
  for idx, word in enumerate(tens):
    numwords[word] = idx * 10
  for idx, word in enumerate(modifiers):
    numwords[word] = idx * .25

  current = 0
  for word in textnum.split():
    if word not in numwords:
        raise ValueError("Illegal word: " + word)
    current += numwords[word]

  return current


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
