import subprocess as sp
import sys
import imp

import Automaton.lib.plugin
import Automaton.lib.settings_loader as settings_loader

def platform():
  return ['linux']

# Requires the program curl to be installed
class Mail(Automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Mail, self).__init__(registrar)
    registrar.register_service("mail", self.execute,
      usage = """
               USAGE: mail
               Checks the gmail account of the user specified in the configuration file.
              """)

  def disable(self):
    self.registrar.unregister_service("mail")

  def execute(self, arg = ''):
    # Load command settings from a configuration file
    cmd_op = settings_loader.load_plugin_settings(__name__)
    if not cmd_op.has_key('MAIL_USER') or not cmd_op.has_key('MAIL_PASS'):
      return "Error: username/password not provided in settings file."
    user = cmd_op["MAIL_USER"]
    pas = cmd_op["MAIL_PASS"]
    cmd ="curl -u "+user+":"+pas+" --silent \"https://mail.google.com/mail/feed/atom\" | tr -d '\n' | awk -F '<entry>' '{for (i=2; i<=NF; i++) {print $i}}' | sed -n \"s/<title>\\(.*\)<\\/title.*name>\\(.*\\)<\\/name>.*/\\2 - \\1/p\""
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
    out, err = p.communicate()
    if out == "":
      out="No mail."
    if len(out) == 0:
        return err
    return out

