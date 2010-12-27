import re
import logger
import settings_loader


class InputSanitizer:

  def __init__(self):
    self.aliases = settings_loader.load_app_settings("InputSanitizer_Aliases")

  def sanitize(self, msg):
    ret = self.alias(msg)
    return ret

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
        cmd, sep, args = self.aliases[match.group(1).upper()].partition(" ")
        try:
          if sep is None:
            ret += self.call(cmd)
          else:
            ret += self.call(cmd, args)
        except Exception, e:
          logger.log("Exception encountered in alias %%%s: %s" %
                                                        (match.group(1), e))
          ret += "%%%s" % match.group(1)
        ret += match.group(2)
      else:
        ret += word
      ret += " "
    return ret

if __name__ == "__main__":
  __name__ == "InputSanitizer"
  i = InputSanitizer()
  def call(s, args = ""):
    if s == "name":
      return "Daniel"
    if s == "me":
      return "Automaton"
    return ""
  i.call = call
  print i.sanitize("Hello, %name. You may call me %me.")
