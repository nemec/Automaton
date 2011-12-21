import os
from automaton.lib import utils, logger, autoplatform


def load_plugin_settings(name):
  """
  Load a plugin's settings.
  Before calling __load_settings it removes the "plugins." package
  indicator.

  """
  name = utils.get_module_name(name)
  name = os.path.join("plugins", name + ".conf")
  return __load_settings(name)

def load_app_settings(name):
  """
  Load an app's settings.
  Remove the absolute path provided by sys.argv in the app and
  remove the .py file extension if it exists.

  """
  name = utils.get_module_name(name)
  name = os.path.join("apps", name + ".conf")
  return __load_settings(name)

def __load_settings(name):
  """
  Private function that loads settings, since both plugins and apps
  have the same settings file format.
  
  """
  opt = {}
  settings = None
  # Try the home directory first, then system, then local settings
  for path in autoplatform.get_dir_hierarchy():
    filepath = os.path.join(path, name)
    if os.path.isfile(filepath):
      with open(filepath, "r") as settings_file:
        settings = settings_file.readlines()
      if settings != None:
        break
  if settings != None:
    for line in settings:
      if len(line.strip()) == 0:
        continue
      # Lines beginning with # are comments
      if line[0] == '#':
        continue
      idx = line.find('=')
      if idx < 0:
        logger.log("Cannot read settings line: " + line)
        continue
      opt[line[0:idx].strip().upper()] = line[idx + 1:].strip()
  return opt
