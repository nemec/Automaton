import re
import logger

class InterpreterRule:
  def __init__(self, command, argrule = None):
    self.command = command
    self.argrule = argrule

  def __str__(self):
    return repr(self.command)

class Interpreter:

  # Grammar Example:
  """
      google{                       # pluginname
        keywords = search | google  # keyword list
        arguments = *               # argument indicator
      }
  """
  # Case sensitive pluginname, 
  # Whitespace unimportant
  # Keywords is the list of keywords recognized as associated with the command
  #  separated by '|'
  # Arguments is an indicator of whether or not the command accepts arguments
  #  Currently, only * and 0 are valid argument indicators
  #  * - all text after the keyword is provided as an argument
  #  0 - this command accepts no arguments

  def __init__(self, services):
    self.grammarDict = {}
    for service in services:
      if hasattr(service, 'grammar'):
        self.addGrammar(service.grammar())

  def recognizedWords(self):
    return self.grammarDict.keys()

  def addGrammar(self, grm):
    grammar = re.sub(r'\s','',grm)
    rx = re.compile( r'(?P<plugin>\w+)\{'
                r'keywords=(?P<kw>\w+(\|\w+)*)'
                r'arguments=(?P<arg>(\w+(\|\w+)*)|\*)'
                r'\}', re.IGNORECASE)
    m = rx.finditer(grammar)
    for x in m:
      for kw in x.group('kw').split('|'):
        if kw not  in self.grammarDict:
          self.grammarDict[kw] = InterpreterRule(x.group('plugin'), x.group('arg'))
        else:
          logger.log("Ambiguous keyword %s for plugin %s." (kw, x.group('plugin')))
          logger.log("Already exists for plugin %s." % self.grammarDict[kw].command)

  # Tidies up the text for better processing, ignoring
  # certain "pretty" words that have no effect on the
  # meaning of the text.
  def cleanSpeech(self, raw):
    raw = re.sub(r'please','',raw) # 'Please' is extraneous speech
    return raw

  # Converts the raw text into a (command, arguments) pair
  # based on the grammar dictionary that was built on initialization
  def interpret(self, raw):
    command = None
    args = None

    raw = self.cleanSpeech(raw)
    
    for key in self.grammarDict:
      ix = raw.find(key)
      if ix >= 0:
        node = self.grammarDict[key]
        command = node.command
        if node.argrule == '*':
          args = raw[ix+len(key):].strip()
        elif node.argrule == '0':
          pass
        else:
          args = raw[ix+len(key):].strip()

    return (command, args)

