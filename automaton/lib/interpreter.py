import re
import nltk
import string

class Interpreter:
  #text = nltk.word_tokenize("What is the weather in Katy, TX like today?")
  #p = nltk.pos_tag(text)

  def __init__(self, registrar):
    self.registrar = registrar
    self.grammarDict = {}

  # Tidies up the text for better processing, ignoring
  # certain "pretty" words that have no effect on the
  # meaning of the text.
  def cleanSpeech(self, raw):
    # Currently does nothing
    return raw

  def best_interpretation(self, raw):
    matches = self.interpret(raw)
    
    if len(matches) == 0:
      return (None, None, None)
    else:
      return matches[0]

  # Converts the raw text into a (command, namespace, arguments) pair
  # based on the grammar dictionary that was built on initialization
  def interpret(self, raw):
    matches = []
    
    similarity_threshold = 0

    tokens = nltk.word_tokenize(raw)
    tagged = nltk.pos_tag(tokens)

    for svc_name in self.registrar.services:
      for ns in self.registrar.services[svc_name]:
        grammar = self.registrar.services[svc_name][ns].grammar
        similarity = self.get_similarity(tagged, grammar, svc_name)
        if similarity > similarity_threshold:
          command = svc_name
          namespace = ns
          args = self.extract_args(tokens, grammar, command)
          matches.append((similarity, (command, namespace, args)))

    matches.sort(key=lambda match: -match[0])
    return [match for score, match in matches]

  def get_similarity(self, tagged_text, grammar, svc_name):
    similarity = 0
    
    if type(grammar) is dict:
      for (idx, (word, pos)) in enumerate(tagged_text):
        if word.lower() == svc_name:  # svc name exists in command
          similarity += 10
          similarity += 15 * ((len(tagged_text) - idx) / float(len(tagged_text)))
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
            op_tok_indices = [idx for (idx, op) in enumerate(tokens) if op == op_tok]
            if op_indices == None:
              op_indices = op_tok_indices
            else:
              op_indices = [idx for idx in op_tok_indices if idx - 1 in op_indices]
          if len(op_indices) > 0:
            indices.append((op_indices[0] - (len(option_tokens) - 1), op_indices[0], arg))

    indices.sort()
    
    for start_idx, end_idx, arg in reversed(indices):
      arg_toks = tokens[end_idx + 1:]
      tokens = tokens[:start_idx]
      args[arg] = " ".join(arg_toks)
    
    return args

if __name__ == "__main__":
  import registrar
  r = registrar.Registrar()
  
  def directions(**kwargs):
    if not all(map(lambda x: x in kwargs, ("from", "to"))):
      return "Missing arguments."
    print "Getting directions from {0} to {1}".format(kwargs["from"], kwargs["to"])
  directions_grammar = {"to":["ending at", "to"], "from":[ "starting at", "from"]}

  def play(**kwargs):
    if "target" not in kwargs:
      print "Missing Arguments"
    print "Playing {0}".format(kwargs["target"])
  play_grammar = {"target":[]}
  
  def play2(**kwargs):
    if "station" not in kwargs:
      print "No station listed."
    print "Loaded station {0}".format(kwargs["station"])
  play2_grammar = {"station": ["station"]}

  def time(**kwargs):
    print "Getting time"

  def stop(**kwargs):
    print "stopping music"

  def weather(**kwargs):
    if not all(map(lambda x: x in kwargs, ("time", "location"))):
      print "Missing arguments"
    print "Getting weather at {0} for {1}".format(kwargs["location"], kwargs["time"])
  weather_grammar = {"location":["at","near","in"], "time": ["for", "be like"]}
    
  r.register_service("directions", directions, directions_grammar, "Gets directions", "ns")
  r.register_service("play", play, play_grammar, "Plays something mon", "ns")
  r.register_service("play", play2, play2_grammar, "A second 'play' service.", "ns2")
  r.register_service("time", time, {}, "gets the time mon", "ns")
  r.register_service("stop", stop, {}, "stops playing music", "ns")
  r.register_service("weather", weather, weather_grammar, "gets the weather mon", "ns")
  
  i = Interpreter(r)
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
