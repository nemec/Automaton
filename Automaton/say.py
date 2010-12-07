import subprocess as sp

class say:

  def execute(self, arg = ''):
      if arg == '':
          return ''
      cmd = '/opt/swift/bin/swift "%s" -o file.wav && sox -V1 file.wav -t wav - trim 8 | aplay -q -; rm file.wav;' %arg
      p = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
      out, err = p.communicate()
      if len(out) == 0:
          return err
      return out

  def platform(self):
    return ['linux']

  def help(self):
    return """
            USAGE: exe command
            Provide a command that will be executed in a spawned shell.
           """

if __name__=="__main__":
  s = say()
  print s.execute("welcome to Automaton, please enjoy your stay")
