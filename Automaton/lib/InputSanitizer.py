import re
import settings_loader


class InputSanitizer:

  def __init__(self):
    self.cmd_op = settings_loader.load_app_settings("InputSanitizer")

  def sanitize(self, msg):
    ret = self.variable_sub(msg)
    return ret

  # Lets you define variables to be replaced with the output of a command.
  # Must be 
  def variable_sub(self, msg):
    ret = ""
    for word in re.split("\s+", msg):
      if word[0] is not "%":
        ret += word
      else:
        word = word[1:]
        # Find consecutive al-num characters in the word
        trigger = re.search("\w+", word)
        if trigger is None: 
          ret += word
        else:
          try:
            key = trigger.group(0)
            if key.upper() in self.cmd_op:
              cmd, sep, args = self.cmd_op[key.upper()].partition(" ")
              # If there is text before or after the key (such as punctuation)
              # add the beginning part to the beginning of the substitution
              beg, extra, end = word.partition(key)
              if extra is not None:
                ret += beg
              if sep is None:
                ret += self.call(cmd)
              else:
                ret += self.call(cmd, args)
              # Add the end of the "extra" text
              if extra is not None:
                ret += end
          except Exception, e:
            print e
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
  print i.sanitize("Hello, %name. You may call me %.me.")
