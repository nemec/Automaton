import subprocess as sp
import re

def execute(arg = ''):
    if arg == '':
      return ''
    p = sp.Popen("dig +short txt \""+arg.replace(" ", "_")+".wp.dg.cx\"", stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
    out, err = p.communicate()
    if len(out) == 0:
        return err
    return out

def help():
  return """
          USAGE: wiki page
          Grabs the beginning of the specified wikipedia page.
         """

