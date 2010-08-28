import lib.settings_loader

#Inserts your specified text into a "memo" textfile
def execute(arg = ''):
  # Load command settings from a configuration file
  cmd_op = settings_loader.load_script_settings(__name__)
  if not cmd_op.has_key('MEMO_FILE'):
    return "Error: no memo file provided in the config."
  f = open(cmd_op['MEMO_FILE'] , "a")
  if arg != '':
      f.write(arg+"\n")
  f.close()
  return "Inserted into memo file."

def platform():
  return ['linux', 'mac', 'windows']

def help():
  return """
          USAGE: memo message
          Appends message to the file specified in the configuration file.
         """

