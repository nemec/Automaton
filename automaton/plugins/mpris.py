import automaton.lib.plugin

try:
  import dbus
except ImportError:
  raise automaton.lib.plugin.PluginLoadError(
    "DBus Python module not installed, but required "
    "for remote control of music.")

# http://dbus.freedesktop.org/doc/dbus-python/doc/tutorial.html
# http://www.mpris.org/1.0/spec


class Music(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Music, self).__init__(registrar)
    
    self.session_bus = dbus.SessionBus()
    self._client = None
    
    registrar.register_service("play", self.play, {"target": []})
    registrar.register_service("listen", self.play, {"target": ["listen to"]})
    registrar.register_service("pause", self.pause, {})
    registrar.register_service("stop", self.stop, {})
    registrar.register_service("song", self.song, {
      "next": ["next"],
      "previous": ["previous"],
    })

  def disable(self):
    self.registrar.unregister_service("play")
    self.registrar.unregister_service("listen")
    self.registrar.unregister_service("pause")
    self.registrar.unregister_service("stop")
    self.registrar.unregister_service("song")

  @property
  def client(self):
    if self._client is None:
      proxy = self.session_bus.get_object(
        'org.mpris.MediaPlayer2.quodlibet', "/Player")
      return dbus.Interface(proxy, dbus_interface="org.freedesktop.MediaPlayer")
    else:
      return self._client

  def song(self, **kwargs):
    if "next" in kwargs:
      self.client.Next()
    elif "previous" in kwargs:
      self.client.Previous()

  def stop(self, **kwargs):
    self.client.Stop()
    
  def pause(self, **kwargs):
    self.client.Pause()

  def play(self, **kwargs):
    if "target" in kwargs:
      pass
    else:
      self.client.Play()


if __name__ == "__main__":
  import automaton.lib.registrar
  r = automaton.lib.registrar.Registrar()
  m = Music(r)
  m.song(next="")
