import os
import re
import utils
import logger
import platformdata

# settings_loader takes a script name, opens the associated settings
# file, and reads all of the settings into a dictionary. It then
# returns the dictionary for use in the program that called the
# function


# Function used by scripts to load their settings
# Before calling __load_settings it removes the "scripts." package
# indicator and prepends cmd_ in case an app and a script have the
# same name
def load_script_settings(scriptname):
  # Removes all "upper" module indicators, if present
  scriptname = utils.get_module_name(scriptname)
  scriptname = os.path.join("commands", scriptname+".conf")
  return __load_settings(scriptname)

# Function used by apps to load their settings
# Before calling __load_settings it removes the absolute path provided
# by sys.argv in the app and removes the .py file extension if it exists.
def load_app_settings(scriptname):
  scriptname = utils.get_module_name(scriptname)
  scriptname = os.path.join("apps", scriptname+".conf")
  return __load_settings(scriptname)

# Private function that loads settings, since both scripts and apps
# have the same settings file format
def __load_settings(scriptname):
  op = {}
  settings = None
  # Try the home directory first, then system, then local settings
  for scriptpath in platformdata.getDirHierarchy():
    filepath = os.path.join(scriptpath,scriptname)
    if os.path.isfile(filepath):
      with open(filepath,"r") as settingsFile:
        settings = settingsFile.readlines()
      if settings != None:
        break
  if scriptname == "memo":
    print settings
  if settings != None:
    for line in settings:
      if len(line.strip()) == 0:
        continue
      # Lines beginning with # are comments
      if line[0]=='#':
        continue
      ix = line.find('=')
      if ix < 0:
        logger.log("Cannot read settings line: "+line)
        continue
      op[line[0:ix].strip().upper()]=line[ix+1:].strip()
  return op
