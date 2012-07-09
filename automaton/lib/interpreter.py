import logger
try:
  import nltk
except ImportError:
  nltk = None
  logger.log("NLTK is not installed, part of speech tagging will not "
    "be included in parsing.")

import string  # pylint: disable-msg=W0402

class Interpreter:
  """
  The interpreter takes natural language and extracts semantic meaning from
  it based on the registered services in the registrar.

  """
  def __init__(self, registrar):
    self.registrar = registrar

  def clean_speech(self, raw):
    """
    Tidy up the text for better processing, ignoring
    certain "pretty" words that have no effect on the
    meaning of the text.
  
    """
    return raw

  def best_interpretation(self, raw):
    matches = self.interpret(raw)
    
    if len(matches) == 0:
      return (None, None, None)
    else:
      return matches[0]

  def interpret(self, raw):
    """
    Convert the raw text into a (command, namespace, arguments) pair
    based on the grammar dictionary that was built on initialization.

    """
    matches = []
    
    similarity_threshold = 0

    if nltk:
      tokens = nltk.word_tokenize(raw)
      tagged = nltk.pos_tag(tokens)
    else:
      import re
      tokens = [token for token in re.split("\s|(\W)", raw) if token]
      tagged = [(token, 'NNP') for token in tokens]

    for svc_name in self.registrar.services:
      for nspc in self.registrar.services[svc_name]:
        grammar = self.registrar.services[svc_name][nspc].grammar
        similarity = self.get_similarity(tagged, grammar, svc_name)
        if similarity > similarity_threshold:
          command = svc_name
          namespace = nspc
          args = self.extract_args(tokens, grammar, command)
          matches.append((similarity, (command, namespace, args)))

    matches.sort(key=lambda match: -match[0])
    return [match for score, match in matches]

  def get_similarity(self, tagged_text, grammar, svc_name):
    """Calculate the similarity between the tagged text and the grammar."""
    # pylint: disable-msg=R0201
    similarity = 0
    
    if type(grammar) is dict:
      for (idx, (word, pos)) in enumerate(tagged_text):
        if word.lower() == svc_name:  # svc name exists in command
          similarity += 10
          similarity += (
            15 * ((len(tagged_text) - idx) / float(len(tagged_text))))
          if pos.startswith("VB"):  # svc name is a verb in command
            similarity += 3
          
        num_args = len(grammar)
        num_match = 0

        if num_args > 0:
          for arg in grammar:
            if (len(grammar[arg]) == 0 and word.lower() == svc_name or
                word.lower() in grammar[arg]):
              num_match += 1

          # 5 * percent of grammar args that show up in command
          # add a little smoothing, to tend towards "more arguments"
          similarity += (5 * (float(num_match) / float(num_args)))

    return similarity

  def extract_args(self, tokens, grammar, command):
    """
    Using the grammar, convert the list of tokens into an argument
    dictionary.

    """
    # pylint: disable-msg=R0201
    args = {}

    tokens = [x.lower() for x in tokens if x not in string.punctuation]
    indices = []

    for arg in grammar:
      if len(grammar[arg]) == 0:
        #arg is unqualified, so find it in tokens
        idx = tokens.index(command)
        indices.append((idx, idx, arg))
      else:
        #arg is qualified, look through all options
        for option in grammar[arg]:
          #look to match option in tokens
          option_tokens = option.split()
          op_indices = None
          for op_tok in option_tokens:
            op_tok_indices = [idx for (idx, op) in 
                                enumerate(tokens) if op == op_tok]
            if op_indices == None:
              op_indices = op_tok_indices
            else:
              op_indices = [idx for idx in
                              op_tok_indices if idx - 1 in op_indices]
          if len(op_indices) > 0:
            indices.append(
              (op_indices[0] - (len(option_tokens) - 1), op_indices[0], arg))

    indices.sort()
    
    for start_idx, end_idx, arg in reversed(indices):
      arg_toks = tokens[end_idx + 1:]
      tokens = tokens[:start_idx]
      args[arg] = " ".join(arg_toks)
    
    return args

#TODO move to unit test
if __name__ == "__main__":
  import registrar
  r = registrar.Registrar()
  i = Interpreter(r)
  
  def directions(**kwargs):
    if not all(map(lambda x: x in kwargs, ("from", "to"))):
      return "Missing arguments."
    print "Getting directions from {0} to {1}".format(kwargs["from"], kwargs["to"])
  directions_grammar = {"to":["ending at", "to"], "from":[ "starting at", "from"]}
  r.register_service("directions", directions, directions_grammar, "Gets directions", "ns")


  def play(**kwargs):
    if "target" not in kwargs:
      print "Missing Arguments"
    print "Playing {0}".format(kwargs["target"])
  play_grammar = {"target":[]}
  r.register_service("play", play, play_grammar, "Plays something mon", "ns")
  
  def play2(**kwargs):
    if "station" not in kwargs:
      print "No station listed."
    print "Loaded station {0}".format(kwargs["station"])
  play2_grammar = {"station": ["station"]}
  r.register_service("play", play2, play2_grammar, "A second 'play' service.", "ns2")


  def time(**kwargs):
    print "Getting time"
  r.register_service("time", time, {}, "gets the time mon", "ns")


  def stop(**kwargs):
    print "stopping music"
  r.register_service("stop", stop, {}, "stops playing music", "ns")


  def weather(**kwargs):
    if not all(map(lambda x: x in kwargs, ("time", "location"))):
      print "Missing arguments"
    print "Getting weather at {0} for {1}".format(kwargs["location"], kwargs["time"])
  weather_grammar = {"location":["at","near","in"], "time": ["for", "be like"]}
  r.register_service("weather", weather, weather_grammar, "gets the weather mon", "ns")
  
  
  def flags(**kwargs):
    if "add" in kwargs:
      print "Adding the flag " + str(kwargs.get("flag", "Unknown"))
    if "remove" in kwargs:
      print "Removing the flag " + str(kwargs.get("flag", "Unknown"))
  flags_grammar = {"add": ["add"], "remove": ["remove"], "flag": [] } 
  r.register_service("flag", flags, flags_grammar, "Tests setting flags as arguments", "ns")


  print i.interpret("I need directions from College Station, TX to Houston, TX")
  print i.interpret("directions from college station, tx to houston, tx")
  print i.interpret("Directions starting at College Station ending at Houston")
  print i.interpret("What time is it?")
  print i.interpret("Please play Led Zeppelin")
  print i.interpret("Play the station Lights")
  print i.interpret("Tell me what time it is.")
  print i.interpret("Will you play Mario Kart?")
  print i.interpret("Please play Ocarina of Time.")
  print i.interpret("Give me directions to Time Square")
  print i.interpret("What time are we going to play football?")
  print i.interpret("Directions starting at college station to houston")
  print i.interpret("What is the weather forecast in College Station for tomorrow?")
  print i.interpret("I would like to know how the weather will be near Houston for today")
  print i.interpret("What will the weather be like tomorrow at Dallas?")  
  print i.interpret("What is the weather like in Snook?")
  print i.interpret("add the flag welcome")
  print i.interpret("remove the flag welcome")
