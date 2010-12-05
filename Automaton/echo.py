
def execute(arg = ''):
    return arg

def grammar():
  return  """
          keywords = echo | repeat
          arguments = *
          """

def help():
  return """
          USAGE: echo message
          Echoes a message back to the user.
         """
