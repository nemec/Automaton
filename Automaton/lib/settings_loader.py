import os
import re
import platform

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
  settings = None
  if platform.system().lower().startswith('windows'):
    personaldir = os.path.join(os.environ['APPDATA'],'automaton')
  else:
    personaldir = os.path.expanduser('~/.automaton/')
  systemdir = os.path.join(__file__[0:__file__.rfind(os.sep)+1],"../settings/")
  # Try the home directory first, then default settings
  for scriptpath in personaldir, systemdir:
    filepath = os.path.join(scriptpath,scriptname+".conf")
    if os.path.isfile(filepath):
      with open(filepath,"r") as settingsFile:
        settings = settingsFile.readlines()
      if settings != None:
        break
  if settings != None:
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
