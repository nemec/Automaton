import time

import automaton.lib.plugin


class GetTime(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(GetTime, self).__init__(registrar)
    
    registrar.register_service("time", self.execute,
      grammar={},
      usage="""
               USAGE: time
               Returns the current time to the user.
              """)
    registrar.register_service("gettime", self.execute,
      grammar={},
      usage="""
               USAGE: gettime
               Returns the current time to the user.
              """)

  def disable(self):
    registrar.unregister_service("time")
    registrar.unregister_service("gettime")

  def execute(self, arg='', **kwargs):
    if arg == "24" or kwargs.get("TYPE", "") == "24":
      return time.strftime("%H:%M")
    else:
      return time.strftime("%I:%M %p")

  def grammar(self):
    return ("gettime{\n"
              "keywords = time\n"
              "arguments = 0\n"
            "}")


if __name__ == "__main__":
  t = GetTime()
  print t.execute()
  print t.execute('24')
