# requires mpd.py from
# http://code.google.com/p/client175/source/browse/trunk/mpd.py
import mpd
import ConfigParser

import automaton.lib.plugin
from automaton.lib import utils, logger


class Music(automaton.lib.plugin.PluginInterface):
  """Plugin that interfaces with MPD to play music."""
  def __init__(self, registrar):
    super(Music, self).__init__(registrar)
    settings = ConfigParser.SafeConfigParser()
    settings.read(utils.get_plugin_settings_paths(__name__))
    hostname = "localhost"
    port = 6600
    try:
      hostname = settings.get("MPD", "hostname")
      port = settings.get("MPD", "port")
    except ConfigParser.NoSectionError:
      raise plugin.PluginLoadError("'MPD' section in config does not exist.")
    except ConfigParser.NoOptionError as e:
      if e.section == "hostname":
        logger.log("MPD hostname not in settings. "
                    "Using default of '{0}'".format(hostname))
      elif e.section == "port":
        logger.log("MPD port not in settings. "
                    "Using default of '{0}'".format(port))
    except TypeError as e:
      logger.log("Error loading settings for MPD. Using host and port "
                  "{0}:{1}.".format(hostname, port))
    self.client = mpd.MPDClient()
    self.client.connect(hostname, port)
    self.version = tuple(int(i) for i in self.client.mpd_version.split('.'))
    
    registrar.register_service("play", self.play,
      {"target": []}, namespace=__name__)
    registrar.register_service("listen", self.play,
      {"target": ["listen to"]}, namespace=__name__)
    registrar.register_service("pause", self.pause, {}, namespace=__name__)
    registrar.register_service("stop", self.stop, {}, namespace=__name__)
    registrar.register_service("song", self.song, {
      "next": ["next"],
      "previous": ["previous"],
    }, namespace=__name__)

  def disable(self):
    """Disable all of Music's services."""
    self.registrar.unregister_service("play", namespace=__name__)
    self.registrar.unregister_service("listen", namespace=__name__)
    self.registrar.unregister_service("pause", namespace=__name__)
    self.registrar.unregister_service("stop", namespace=__name__)
    self.registrar.unregister_service("song", namespace=__name__)

  def can_find(self):
    """Return whether or not the connected version of MPD has the
    capabilities to search for music.

    """
    return not ((self.version[0] == 0) and (self.version[1] < 16))

  def song(self, **kwargs):
    """Performs actions on the media player.
    
    Keyword arguments:
    next -- if exists, go to the next song
    previous -- if exists, go to the previous song

    """
    if "next" in kwargs:
      self.client.next()
    elif "previous" in kwargs:
      self.client.previous()

  def stop(self, **kwargs):
    """Stop playing music."""
    self.client.stop()
    
  def pause(self, **kwargs):
    """Pause/play the current song in MPD."""
    self.client.pause()

  def play(self, **kwargs):
    """Play a song in MPD.

    Keyword arguments:
    target -- the artist/album to put in the playlist before playing
      (defaults to the current playlist)

    """
    if "target" in kwargs:
      # Format of "play artist/album"
      if(self.can_find() and 
          kwargs["target"] is not None and
          len(kwargs["target"]) > 0):
        self.client.clear()
        for song in self.client.search("artist", kwargs["target"]):
          try:
            self.client.add(song['file'])
          except Exception:
            print "Could not add song {0}".format(song)
        self.client.play()
    # Play whatever's in there
    else:
      state = self.client.status()['state']
      if state == "stop":
        self.client.play()
      elif state == "pause":
        self.client.pause()
