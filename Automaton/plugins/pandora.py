import socket

import Automaton.lib.plugin
import Automaton.lib.settings_loader as settings_loader

class Pandora(Automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Pandora, self).__init__(registrar)
    cmd_op = {"ip":"localhost", "port":"9900"}
    cmd_op.update(settings_loader.load_plugin_settings(__name__))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((cmd_op["ip"], int(cmd_op["port"])))

    registrar.register_service("pandora", self.execute,
      usage = """
               USAGE: pandora command
               Connects to the local Pandora client and sends a command to it
              """)

  def disable(self):
    self.registrar.unregister_service("pandora")

  def execute(self, arg = ''):
    sock.send(arg)
    response = sock.recv(1024)
    return response

  def grammar(self):
    return  "pandora{"+\
              "keywords = pandora"+\
              "arguments = *"+\
            "}"

