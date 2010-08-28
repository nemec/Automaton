import subprocess as sp

def execute(arg = ''):
    if arg == '':
        return help()

    ix = arg.rfind(' at')
    if arg.find(' at') < 0:
      return help()
    ix2 = arg.find(' ')
    cmd = arg[0:ix2]
    args = arg[ix2+1:ix]
    time = arg[ix+1:].strip()
    frlist = 'scripts.'+cmd
    try:
      __import__(frlist)
    except ImportError:
      return "Command not found.\nDid you forget to import it?"
    print cmd
    print args
    print time
    line = "python %s %s %s | %s" % (__file__,cmd, args, time)
    print line
    p = sp.Popen(line, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
    out, err = p.communicate()
    if len(out) == 0:
        return err
    return out

def platform():
  return ['linux']

def help():
  return "USAGE: run [script] at [time]\nThe specified script will be run at the provided time."

if __name__ == "__main__":
  import sys
  cmd = sys.argv[1]
  try:
    __import__(cmd)
  except ImportError:
    print "run: error executing the "+cmd+" script."
    sys.exit()
  if len(sys.argv) > 2:
    sys.modules[cmd].execute(" ".join(sys.argv[2:]))
  else:
    print sys.modules[cmd].execute()
