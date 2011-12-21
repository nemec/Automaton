import subprocess as sp

import automaton.lib.plugin as plugin
import automaton.lib.settings_loader as settings_loader


def platform():
  """Return the list of platforms the plugin is available for."""
  return ['linux']


# Requires the program curl to be installed
class Mail(plugin.PluginInterface):
  """Plugin that retrieves a user's email through IMAP."""

  def __init__(self, registrar):
    super(Mail, self).__init__(registrar)
    registrar.register_service("mail", self.execute,
      grammar={},
      usage=("USAGE: %s\n"
             "Checks the gmail account of the user specified in "
             "the configuration file."),
      namespace=__name__)

  def disable(self):
    """Disable all of Mail's services."""
    self.registrar.unregister_service("mail", namespace=__name__)

  def execute(self, **kwargs):
    """Retrieve mail from a GMail account through curl."""

    # Load command settings from a configuration file
    cmd_op = settings_loader.load_plugin_settings(__name__)
    if not 'MAIL_USER' in cmd_op or not 'MAIL_PASS' in  cmd_op:
      raise plugin.UnsuccessfulExecution("Error: username/password "
                                          "not provided in settings file.")
    user = cmd_op["MAIL_USER"]
    pas = cmd_op["MAIL_PASS"]
    cmd = ("curl -u {0}:{1} --silent \"https://mail.google.com/mail/"
            "feed/atom\" | tr -d '\n' | awk -F '<entry>' '{"
            "for (i=2; i<=NF; i++) {print $i}}' | "
            "sed -n \"s/<title>\\(.*\)<\\/title.*name>\\(.*\\)"
            "<\\/name>.*/\\2 - \\1/p\"".format(user, pas))
    proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
    out, err = proc.communicate()
    if out == "":
      out = "No mail."
    if len(out) == 0:
      raise plugin.UnsuccessfulExecution(err)
    return out
