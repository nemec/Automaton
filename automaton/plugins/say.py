import os
import tempfile
import gst
import gobject
#import threading
import subprocess as sp

import automaton.lib.plugin
import automaton.lib.autoplatform as autoplatform

gobject.threads_init()


def platform():
  """Return the list of platforms the plugin is available for."""
  return ['linux']


class Say(automaton.lib.plugin.PluginInterface):
  """Speak the provided text through the computer's speakers."""
  def __init__(self, registrar):
    super(Say, self).__init__(registrar)
    registrar.register_service("say", self.execute,
      grammar={"text": []},
      usage=("USAGE: say text\n"
             "Speaks the provided text to the speakers."),
      namespace=__name__)

  def disable(self):
    """Disable all of Say's services."""
    self.registrar.unregister_service("say", namespace=__name__)

  def execute(self, **kwargs):
    """Speak the provided text through the computer's speakers.

    Keyword arguments:
    text -- the text to speak

    """
    if "text" not in kwargs:
      return ''
    phrase = str(kwargs["text"])
    
    names = {
      "callie": "6.5",
      "lawrence": "8.5"
    }
    name = "callie"

    #TODO find a better way of implementing TTS
    ttsfd, ttsfile = tempfile.mkstemp(".wav")
    outfile, outname = tempfile.mkstemp(".wav")
    try:
      
      tts = sp.Popen(['/opt/swift/bin/swift', '-o', ttsfile, '-n', name, phrase], stdout=sp.PIPE, stderr=sp.PIPE)
#      cmd = ('/opt/swift/bin/swift "' + phrase + '" -o ' + ttsname + ' && sox -V1 ' +
#             tmp + ' -t wav ' + tmp2 + ' trim 8 ;')
#      p = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True)
#      out, err = p.communicate()
#      if len(err) > 0:
#        return err

      out, err = tts.communicate()
      if not err:
        sox = sp.Popen(['sox', '-V1', ttsfile, '-t', 'wav', outname, 'trim', names[name]], stdout=sp.PIPE, stderr=sp.PIPE)
        out, err = sox.communicate()

      player = gst.element_factory_make("playbin2", "player")
      bus = player.get_bus()
      bus.add_signal_watch()

      mainloop = gobject.MainLoop()

      def quit(bus, message):
        mainloop.quit()

      bus.connect("message::eos", quit)
      bus.connect("message::error", quit)
      player.set_property("uri", 'file://' + outname)
      player.set_state(gst.STATE_PLAYING)

      try:
        mainloop.run()
      finally:
        player.set_state(gst.STATE_NULL)

    finally:
      try:
        os.remove(ttsfile)
      except OSError as err:
        print e
      try:
        os.remove(outname)
      except IOError as err:
        print err

if __name__ == "__main__":
  from automaton.lib import registrar
  r = registrar.Registrar()
  s = Say(r)
  s.execute(text="this is awesome")
