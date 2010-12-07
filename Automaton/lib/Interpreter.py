import re

class rule:
  def __init__(self, command, argrule = None):
    self.command = command
    self.argrule = argrule

  def __str__(self):
    return repr(self.command)

def interpret(raw, services):
  command = None
  args = None
  grammar = ''

  for service in services:
    try:
      grammar = grammar + service.grammar()
    except AttributeError:
      pass

  gram = re.sub(r'\s','',grammar)
  rx = re.compile( r'(?P<script>\w+)\{'
              r'keywords=(?P<kw>\w+(\|\w+)*)'
              r'arguments=(?P<arg>(\w+(\|\w+)*)|\*)'
              r'\}', re.IGNORECASE)
  m = rx.finditer(gram)
  tree = {}
  for x in m:
    for kw in x.group('kw').split('|'):
      if not tree.has_key(kw):
        tree[kw] = rule(x.group('script'), x.group('arg'))
      else:
        print "Ambiguous keyword %s for script %s." (kw, x.group('script'))

  raw = re.sub(r'please','',raw)
  for key in tree.keys():
    ix = raw.find(key)
    if ix >= 0:
      node = tree[key]
      command = node.command
      if node.argrule == '*':
        args = raw[ix+len(key):].strip()
      elif node.argrule == '0':
        pass
      else:
        args = raw[ix+len(key):].strip()
  return (command, args)

