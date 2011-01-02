import platform as pl
import os

# This module deals with platform-specific paths

# Set the platform we are currently running on
if pl.system().lower().startswith('windows'):
  platform =  'windows'
elif pl.system().lower().startswith('darwin'):
  platform = 'mac'
else:
  platform = 'linux'

def getDirHierarchy():
  return (personaldir(), systemdir(), localdir())

# The personal directory for settings storage.
# The settings location in the "home" directory for a user.
def personaldir():
  if platform == 'windows':
    return os.path.join(os.environ['APPDATA'],'automaton')
  else:
    return os.path.expanduser('~/.automaton/')

# The system directory for settings storage.
# Usually the default "/etc" directory.
def systemdir():
  if platform == 'windows':
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

