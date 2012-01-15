import re
import ConfigParser

from automaton.lib import logger, utils


class InputSanitizer:
  """Class for cleaning and modifying text."""
  def __init__(self, registrar):
    self.registrar = registrar
    settings = ConfigParser.SafeConfigParser()
    settings.read(utils.get_app_settings_paths(__name__))
    self.aliases = {'PREV': ""}
    try:
      self.aliases = dict((key.upper(), tuple(value)) for key, value in
        settings.items("Aliases"))
    except ConfigParser.NoSectionError:
      logger.log("No section 'Aliases' found in input_sanitizer config file.")

  def sanitize(self, msg):
    """Clean up the message."""
    ret = self.alias(msg)
    return ret.strip()

  def alias(self, msg):
    """
    Lets you define variables to be replaced with the output of a command.
    Must begin with a % and contain only alphanumeric characters. The alias
    name will end when non-alphanumeric characters are encountered (including
    punctuation and whitespace). Configuration examples are found in
    InputSanitizer_Aliases.conf

    """
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
        except Exception as err:
          logger.log("Exception encountered in alias "
                     "%%{0}: {1}".format(match.group(1), err))
          ret += "%%{0}".format(match.group(1))
        ret += match.group(2)
      else:
        ret += word
      ret += " "
    return ret

  def set_prev_alias(self, alias):
    """
    Defines a special "prev" alias that contains the output of the last
    command run

    """
    self.aliases['PREV'] = "echo " + alias

#TODO Move to unit test
"""if __name__ == "__main__":
  __name__ == "InputSanitizer"
  i = InputSanitizer()

  def call(s, args=""):
    if s == "name":
      return "Tim"
    if s == "me":
      return "Automaton"
    return ""

  print i.sanitize("Hello, %name. You may call me %me.")"""
