import subprocess as sp
import gst
import threading
import lib.platformdata as platformdata
import os
import gobject

gobject.threads_init()

class say:

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

  def platform(self):
    return ['linux']

  def help(self):
    return """
            USAGE: exe command
            Provide a command that will be executed in a spawned shell.
           """

if __name__=="__main__":
  s = say()
  print s.execute("welcome to Automaton, please enjoy your stay")
