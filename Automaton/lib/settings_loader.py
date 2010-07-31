import os
import re

# settings_loader takes a script name, opens the associated settings
# file, and reads all of the settings into a dictionary. It then
# returns the dictionary for use in the program that called the
# function


# Function used by scripts to load their settings
# Before calling __load_settings it removes the "scripts." package
# indicator and prepends cmd_ in case an app and a script have the
# same name
def load_script_settings(scriptname):
  scriptname = scriptname[scriptname.rfind('.')+1:]
  return __load_settings('cmd_'+scriptname)

# Function used by apps to load their settings
# Before calling __load_settings it removes the absolute path provided
# by sys.argv in the app and removes the .py file extension if it exists.
def load_app_settings(scriptname):
  scriptname = os.path.basename(scriptname)
  regex = re.compile('\.py$')
  scriptname = regex.sub('', scriptname)
  return __load_settings(scriptname)

# Private function that loads settings, since both scripts and apps
# have the same settings file format
def __load_settings(scriptname):
  op = {}
  # format scriptname if we're given a path
  scriptpath = __file__[0:__file__.rfind('/')+1]+"../settings/"
  with open(scriptpath+scriptname+".conf","r") as settingsFile:
    settings = settingsFile.readlines()
  for line in settings:
    # Lines beginning with # are comments
    if line[0]=='#':
      continue
    ix = line.find('=')
    if ix < 0:
      log("Cannot read settings line: "+line)
      continue
    op[line[0:ix].strip().upper()]=line[ix+1:].strip()
  return op
