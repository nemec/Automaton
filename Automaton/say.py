import subprocess as sp

def execute(arg = ''):
    if arg == '':
        return ''
    cmd = '/opt/swift/bin/swift "%s" -o file.wav && sox file.wav out.wav trim 8 255 && mplayer out.wav; rm file.wav out.wav;' %arg
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
    out, err = p.communicate()
    if len(out) == 0:
        return err
    return out

def help():
  return """
          USAGE: exe command
          Provide a command that will be executed in a spawned shell.
         """
