import automaton.lib.plugin

try:
  import dbus
except ImportError:
  raise automaton.lib.plugin.PluginLoadError(
    "DBus Python module not installed, but required "
    "for remote control of music.")

# http://dbus.freedesktop.org/doc/dbus-python/doc/tutorial.html
# http://www.mpris.org/1.0/spec


class Mpris(automaton.lib.plugin.PluginInterface):
  """Plugin that adds MPRIS support for Automaton."""
  def __init__(self, registrar):
    super(Mpris, self).__init__(registrar)
    
    self.session_bus = dbus.SessionBus()
    self._client = None
    
    registrar.register_service("play", self.play, {"target": []},
      namespace=__name__)
    registrar.register_service("listen", self.play, {"target": ["listen to"]},
      namespace=__name__)
    registrar.register_service("pause", self.pause, {}, namespace=__name__)
    registrar.register_service("stop", self.stop, {}, namespace=__name__)
    registrar.register_service("song", self.song, {
      "next": ["next"],
      "previous": ["previous"],
    },
    namespace=__name__)

  def disable(self):
    """Disable all of Mpris' services."""
    self.registrar.unregister_service("play")
    self.registrar.unregister_service("listen")
    self.registrar.unregister_service("pause")
    self.registrar.unregister_service("stop")
    self.registrar.unregister_service("song")

  @property
  def client(self):
    """Return the MPRIS client for the running media player."""
    if self._client is None:
      proxy = self.session_bus.get_object(
        'org.mpris.MediaPlayer2.quodlibet', "/Player")
      return dbus.Interface(proxy, dbus_interface="org.freedesktop.MediaPlayer")
    else:
      return self._client

  def song(self, **kwargs):
    """Perform actions on the playlist.

    Keyword arguments:
    next -- if passed in as a keyword argument, move to the next song
    previous -- if passed in as a keyword argument, move to the previous song

    """
    if "next" in kwargs:
      self.client.Next()
    elif "previous" in kwargs:
      self.client.Previous()

  def stop(self, **kwargs):
    """Stop playing music."""
    self.client.Stop()
    
  def pause(self, **kwargs):
    """Play/pause the current song."""
    self.client.Pause()

  def play(self, **kwargs):
    """Play a song.

    Keyword arguments:
    target -- add all songs that match the value of target to the playlist,
      then play (default to adding no songs)

    """
    if "target" in kwargs:
      pass
    else:
      self.client.Play()
