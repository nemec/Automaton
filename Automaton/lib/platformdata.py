import platform
import os

# This module deals with platform-specific paths

def getDirHierarchy():
  return (personaldir(), systemdir(), localdir())

# The personal directory for settings storage.
# The settings location in the "home" directory for a user.
def personaldir():
  if getPlatform() == 'windows':
    return os.path.join(os.environ['APPDATA'],'automaton')
  else:
    return os.path.expanduser('~/.automaton/')

# The system directory for settings storage.
# Usually the default "/etc" directory.
def systemdir():
  if getPlatform() == 'windows':
    return ""
  else:
    return "/etc/automaton/"

# The local directory for settings storage.
# Located in the same place as the rest of the Automaton modules
def localdir():
  # Method for getting dir taken from wxPython project
  root = __file__
  if os.path.islink (root):
    root = os.path.realpath (root)
  directory = os.path.dirname (os.path.abspath (root))
  return os.path.join(directory ,"../settings/")

def getPlatform():
  if platform.system().lower().startswith('windows'):
    return 'windows'
  elif platform.system().lower().startswith('darwin'):
    return 'mac'
  else:
    return 'linux'

os.access("/etc/automaton", os.R_OK)
