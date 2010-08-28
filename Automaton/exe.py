import subprocess as sp

def execute(arg = ''):
    if arg == '':
        return ''
    p = sp.Popen(arg, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
    out, err = p.communicate()
    if len(out) == 0:
        return err
    return out

def platform():
  return ['linux', 'mac', 'windows']

def help():
  return """
          USAGE: exe command
          Provide a command that will be executed in a spawned shell.
         """
