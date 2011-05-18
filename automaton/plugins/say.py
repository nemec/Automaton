import subprocess as sp
import gst
import threading
import os
import gobject

import automaton.lib.plugin
import automaton.lib.platformdata as platformdata

gobject.threads_init()


def platform():
  return ['linux']

class Say(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Say, self).__init__(registrar)
    registrar.register_service("say", self.execute,
      usage = """
               USAGE: say text
                      Speaks the provided text to the speakers.
              """)

  def disable(self):
    self.registrar.unregister_service("say")

  def execute(self, arg = ''):
    if arg == '':
      return ''
    tmp = platformdata.getExistingFile("say.wav")
    tmp2 = platformdata.getExistingFile("say2.wav")
    ## aplay, mplayer, etc all hang for >5 sec after playing, so gstreamer
    ## is used to significantly reduce that time
    #cmd = ('/opt/swift/bin/swift "'+arg+'" -o '+tmp+' && sox -V1 '+tmp+
    #      ' -t wav - trim 8 | aplay -q -; rm '+tmp+';')
    cmd = ('/opt/swift/bin/swift "'+arg+'" -o '+tmp+' && sox -V1 '+tmp+
          ' -t wav '+tmp2+' trim 8 ;')
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr = sp.PIPE, shell = True)
    out, err = p.communicate()
    if len(err) > 0:
      return err

    os.remove(tmp)

    player = gst.element_factory_make("playbin2", "player")
    bus = player.get_bus()
    bus.add_signal_watch()

    mainloop = gobject.MainLoop()

    def quit(bus, message):
      mainloop.quit()

    bus.connect("message::eos", quit)
    bus.connect("message::error", quit)
    player.set_property("uri", 'file://'+tmp2)
    player.set_state(gst.STATE_PLAYING)
    

    try:
      mainloop.run()
    finally:
      player.set_state(gst.STATE_NULL)

    os.remove(tmp2)
    return ""

