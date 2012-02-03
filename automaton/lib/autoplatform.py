import platform as pl
import os

# pylint: disable-msg=C0103
# This module deals with platform-specific paths

# Set the platform we are currently running on
if pl.system().lower().startswith('windows'):
  platform = 'windows'
elif pl.system().lower().startswith('darwin'):
  platform = 'mac'
else:
  platform = 'linux'


def get_dir_hierarchy():
  """An ordered hierarchy of directories to use."""
  return (personaldir(), systemdir(), localdir())


def personaldir():
  """
  The personal directory for settings storage.
  The settings location in the "home" directory for a user.

  """
  if platform == 'windows':
    return os.path.join(os.environ['APPDATA'], 'automaton')
  else:
    return os.path.expanduser('~/.automaton/')

def systemdir():
  """
  The system directory for settings storage.
  Usually the default "/etc" directory.

  """
  if platform == 'windows':
    return os.path.join(os.environ['ProgramFiles'], 'automaton')
  else:
    return "/etc/automaton/"

def localdir():
  """
  The local directory for settings storage.
  Located in the same place as the rest of the Automaton modules.
  Method for getting dir taken from wxPython project

  """
  root = __file__
  if os.path.islink(root):
    root = os.path.realpath(root)
  directory = os.path.dirname(os.path.abspath(root))
  return os.path.normpath(os.path.join(directory, "../settings/"))

def get_existing_file(filename, strict=False):
  """
  Searches through the directory hierarchy for a file/path named "filename"
  If 'strict' is false, it returns a path where the file can be placed if there
  is no existing file.
  If 'strict' is true, returns None there is no existing file.

  """
  path = None
  # First check to see if the queue file exists anywhere
  for d in get_dir_hierarchy():
    if os.path.exists(d):
      filepath = os.path.join(d, filename)
      if os.access(filepath, os.W_OK):
        path = filepath
        break
  # Now try to create a queue file in one of the dirs
  if path is None and not strict:
    for directory in get_dir_hierarchy():
      if not os.path.exists(directory):
        try:
          os.mkdir(directory)
        except IOError:
          pass
      filepath = os.path.join(directory, filename)
      if os.access(directory, os.W_OK):
        path = filepath
        break
  return path
