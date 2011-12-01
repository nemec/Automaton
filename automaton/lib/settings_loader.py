import os
import re
import utils
import logger
import autoplatform

# settings_loader takes a plugin name, opens the associated settings
# file, and reads all of the settings into a dictionary. It then
# returns the dictionary for use in the program that called the
# function


# Function used by plugins to load their settings
# Before calling __load_settings it removes the "plugins." package
# indicator and prepends cmd_ in case an app and a plugin have the
# same name
def load_plugin_settings(name):
  # Removes all "upper" module indicators, if present
  name = utils.get_module_name(name)
  name = os.path.join("plugins", name + ".conf")
  return __load_settings(name)


# Function used by apps to load their settings
# Before calling __load_settings it removes the absolute path provided
# by sys.argv in the app and removes the .py file extension if it exists.
def load_app_settings(name):
  name = utils.get_module_name(name)
  name = os.path.join("apps", name + ".conf")
  return __load_settings(name)


# Private function that loads settings, since both plugins and apps
# have the same settings file format
def __load_settings(name):
  op = {}
  settings = None
  # Try the home directory first, then system, then local settings
  for path in autoplatform.getDirHierarchy():
    filepath = os.path.join(path, name)
    if os.path.isfile(filepath):
      with open(filepath, "r") as settingsFile:
        settings = settingsFile.readlines()
      if settings != None:
        break
  if settings != None:
    for line in settings:
      if len(line.strip()) == 0:
        continue
      # Lines beginning with # are comments
      if line[0] == '#':
        continue
      ix = line.find('=')
      if ix < 0:
        logger.log("Cannot read settings line: " + line)
        continue
      op[line[0:ix].strip().upper()] = line[ix + 1:].strip()
  return op
