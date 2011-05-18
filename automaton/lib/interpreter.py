import re
import nltk
import automaton.lib.logger

class InterpreterRule:
  def __init__(self, command, argrule = None):
    self.command = command
    self.argrule = argrule

  def __str__(self):
    return repr(self.command)

class Interpreter:
  #text = nltk.word_tokenize("What is the weather in Katy, TX like today?")
  #p = nltk.pos_tag(text)

  def __init__(self, registrar):
    self.registrar = registrar
    self.grammarDict = {}
  #  self.init_grammars()

  #def init_grammars(self):
  #  for svc in self.registrar.services:
  #    self.grammarDict

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
          logger.log("Ambiguous keyword {0} for plugin {1}.".format(kw, x.group('plugin')))
          logger.log("Already exists for plugin {0}.".format(self.grammarDict[kw].command))

  # Tidies up the text for better processing, ignoring
  # certain "pretty" words that have no effect on the
  # meaning of the text.
  def cleanSpeech(self, raw):
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

