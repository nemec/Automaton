# requires mpd.py from
# http://code.google.com/p/client175/source/browse/trunk/mpd.py
import mpd

import automaton.lib.plugin


class Music(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Music, self).__init__(registrar)
    self.client = mpd.MPDClient()
    self.client.connect("localhost", 6600)
    self.version = map(lambda x: int(x), self.client.mpd_version.split('.'))

    #registrar.register_service("music", self.execute, {"target": []},
    #  usage="""
    #         USAGE: music [play|pause|stop]
    #         Controls an mpd server
    #        """)
    
    registrar.register_service("play", self.play, {"target": []})
    registrar.register_service("pause", self.pause, {})
    registrar.register_service("stop", self.stop, {})

  def disable(self):
    self.registrar.unregister_service("music")

  def canFind(self):
    return not ((self.version[0] == 0) and (self.version[1] < 16))

  def play(self, arg='', **kwargs):
    if not "target" in kwargs:
      return "No target provided."
    self.execute("play " + kwargs["target"])

  def stop(self, arg='', **kwargs):
    self.client.stop()
    
  def pause(self, arg='', **kwargs):
    self.client.pause()

  def execute(self, arg='', **kwargs):
    print arg
    if arg.startswith("play"):
      # Format of "play artist/album"
      search = arg[4:].strip()
      if self.canFind() and len(search) > 0:
        self.client.clear()
        for song in self.client.search("artist", search):
          print song
          try:
            self.client.add(song['file'])
          except:
            print "Could not add song {0}".format(song)
        self.client.play()
      # Play whatever's in there
      else:
        state = self.client.status()['state']
        if state == "stop":
          self.client.play()
        elif state == "pause":
          self.client.pause()

    elif arg.startswith("stop"):
      self.client.stop()

    elif arg.startswith("pause"):
      self.client.pause()
    return ""

  def grammar(self):
    return ("music{\n"
              "keywords = music | sound\n"
              "arguments = *\n"
            "}")
