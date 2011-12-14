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
    
    registrar.register_service("play", self.play, {"target": []}, namespace=__name__)
    registrar.register_service("listen", self.play, {"target": ["listen to"]}, namespace=__name__)
    registrar.register_service("pause", self.pause, {}, namespace=__name__)
    registrar.register_service("stop", self.stop, {}, namespace=__name__)
    registrar.register_service("song", self.song, {
      "next": ["next"],
      "previous": ["previous"],
    }, namespace=__name__)

  def disable(self):
    self.registrar.unregister_service("play", namespace=__name__)
    self.registrar.unregister_service("listen", namespace=__name__)
    self.registrar.unregister_service("pause", namespace=__name__)
    self.registrar.unregister_service("stop", namespace=__name__)
    self.registrar.unregister_service("song", namespace=__name__)

  def canFind(self):
    return not ((self.version[0] == 0) and (self.version[1] < 16))

  def song(self, **kwargs):
    if "next" in kwargs:
      self.client.next()
    elif "previous" in kwargs:
      self.client.previous()

  def stop(self, **kwargs):
    self.client.stop()
    
  def pause(self, **kwargs):
    self.client.pause()

  def play(self, **kwargs):
    if "target" in kwargs:
      # Format of "play artist/album"
      if self.canFind() and len(kwargs["target"]) > 0:
        self.client.clear()
        for song in self.client.search("artist", kwargs["target"]):
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
