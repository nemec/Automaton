import time

class gettime:

  def execute(self, arg = ''):
    if arg == "24":
      return time.strftime("%H:%M")
    else:
      return time.strftime("%I:%M %p")

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
