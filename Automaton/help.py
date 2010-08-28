import sys

def execute(arg = ''):
  if arg is '' or arg == 'help':
    return "USAGE: help cmd\n"+\
           "Provides a short usage for the command along with a description."
  if arg.find(' ') > 0:
    frlist = 'scripts.'+arg[0:arg.find(' ')]
  else:
    frlist = 'scripts.'+arg
  try:
    __import__(frlist)
  except ImportError:
    return "Command not found.\nDid you forget to import it?"
  return sys.modules[frlist].help()

def platform():
  return ['linux', 'mac', 'windows']

