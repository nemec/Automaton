class echo:

  def execute(self, arg = ''):
    return arg

  def grammar(self):
    return  "echo{"+\
              "keywords = echo | repeat"+\
              "arguments = *"+\
            "}"

  def help(self):
    return """
            USAGE: echo message
            Echoes a message back to the user.
           """
