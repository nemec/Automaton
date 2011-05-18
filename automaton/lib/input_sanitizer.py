import re
import logger
import settings_loader


class InputSanitizer:

  def __init__(self, registrar):
    self.registrar = registrar
    self.aliases = settings_loader.load_app_settings("InputSanitizer_Aliases")
    self.aliases['PREV'] = ""

  def sanitize(self, msg):
    ret = self.alias(msg)
    return ret.strip()

  # Lets you define variables to be replaced with the output of a command.
  # Must begin with a % and contain only alphanumeric characters. The alias
  # name will end when non-alphanumeric characters are encountered (including
  # punctuation and whitespace). Configuration examples are found in
  # InputSanitizer_Aliases.conf
  def alias(self, msg):
    ret = ""
    for word in re.split("\s+", msg):
      match = re.match("%(\w+)(.*)", word)
      if match:
        name = match.group(1).upper()
        if name in self.aliases:
          cmd, sep, args = self.aliases[name].partition(" ")
        elif name in self.registrar.services:
          cmd, sep, args = (name, None, None)
        try:
          if sep is None:
            ret += self.registrar.request_service(cmd)
          else:
            ret += self.registrar.request_service(cmd, args)
        except Exception as e:
          logger.log("Exception encountered in alias "
                     "%%{0}: {1}".format(match.group(1), e))
          ret += "%%{0}".format(match.group(1))
        ret += match.group(2)
      else:
        ret += word
      ret += " "
    return ret

  # Defines a special "prev" alias that contains the output of the last
  # command run
  def set_prev_alias(self, alias):
    self.aliases['PREV'] = "echo " + alias

if __name__ == "__main__":
  __name__ == "InputSanitizer"
  i = InputSanitizer()
  def call(s, args = ""):
    if s == "name":
      return "Tim"
    if s == "me":
      return "Automaton"
    return ""
  print i.sanitize("Hello, %name. You may call me %me.")
