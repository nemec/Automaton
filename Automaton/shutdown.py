import subprocess as sp

# Shuts down the host computer in the specified number of seconds
def execute(arg = 'now'):
    try:
        int(arg)
    except ValueError:  # arg is not int
        try:
            if arg.find(':') > 0: # Possibly in hh:mm format
                int(arg.split(':')[0])+int(arg.split(':')[1])
            elif not arg == 'now': # Otherwise must be 'now'
                return ''
        except ValueError:
            return ''        
        
    p = sp.Popen('shutdown -P ' + arg, stdout = sp.PIPE, shell = True)
    return p.communicate()[0]

def help():
  return """
          USAGE: shutdown when
          Shuts down the computer at the specified time. Defaults to now.
         """

