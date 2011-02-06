# requires mpd.py from http://code.google.com/p/client175/source/browse/trunk/mpd.py
import mpd

class music:
  def __init__(self):
    self.client = mpd.MPDClient()
    self.client.connect("localhost",6600)
    self.version = map(lambda x: int(x), self.client.mpd_version.split('.'))

  def canFind(self):
    return not ((self.version[0] == 0) and (self.version[1] < 16))

  def execute(self, arg = ''):
    if arg.startswith("play"):
      # Format of "play artist/album"
      search = arg[4:].strip()
      if self.canFind() and len(search) > 0:
        self.client.clear()
        print "sfdds"
        for song in self.client.search("artist", search):
          print song
          try:
            self.client.add(song['file'])
          except:
            print "Could not add song %s" % song
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
    return  "music{"+\
              "keywords = music | sound"+\
              "arguments = *"+\
            "}"

  def help(self):
    return """
            USAGE: music [play|pause|stop]
            Controls an mpd server
           """
