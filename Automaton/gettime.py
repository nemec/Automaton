from time import localtime

class gettime:

  def execute(self, arg = ''):
    t = localtime()
    ampm = ''
    hours = t.tm_hour
    if not arg == '24':
      if hours < 12:
        ampm = "A.M."
      else:
        ampm = "P.M."
      if hours > 12:
        hours = hours - 12
      if hours == 0:
        hours = 12
    return "%s:%s %s" % (hours, t.tm_min, ampm)

  def grammar(self):
    return  "gettime{"+\
              "keywords = time"+\
              "arguments = 0"+\
            "}"

  def help(self):
    return """
            USAGE: time
            Returns the current time to the user.
           """

if __name__=="__main__":
  t = gettime()
  print t.execute()
  print t.execute('24')
