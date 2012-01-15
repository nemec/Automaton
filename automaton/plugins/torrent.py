import re
import urllib
import urllib2
import os.path
import ConfigParser
import subprocess as sp
from BeautifulSoup import BeautifulSoup

from automaton.lib import plugin, logger, utils


class Torrent(plugin.PluginInterface):
  """Plugin for searching for and starting torrents."""
  search_urls = {
    "pirate_bay": "http://thepiratebay.org/search.php?q={0}",
  }

  def search(self, name):
    """Perform a search through each of the provided search urls for the
    given name. Return a list of .torrent files.

    """
    results = []
    for url in self.search_urls.values():
      try:
        page = urllib.urlopen(url.format(name)).read()
        soup = BeautifulSoup(page)
        table = soup.find('table').findAll('tr')
        #soup.findAll(attrs={'class':"vertTh"})
        for result in table:
          if str(result) != "\n" and not result.attrs:
            vals = result.findAll('td')
            if len(vals) == 4:
              seeders = int(vals[2].contents[0])
              leechers = int(vals[3].contents[0])
              info = vals[1].findNext('a')
              #title = dict(info.attrs)['title']
              #details = "Details for "
              #if title.startswith(details):
              #  title = title[len(details):]
              link = dict(info.findNext('a').attrs)['href']
              results.append((seeders, link))
      except Exception as err:
        logger.log("Error performing torrent search", err)
        continue
      top = None
      try:
        top = max(results)[1]
      except ValueError:
        pass
      return top

  def begin_torrent(self, movie_name):
    """Attempt to start a torrent program to begin download of the torrent."""
    filename = os.path.join(self.settings.get("Downloads", "download_dir"),
                                                  os.path.basename(movie_name))
    try:
      urllib.urlretrieve(movie_name, filename)
    except IOError as err:
      logger.log("Error downloading torrent:", err)
      raise Exception("Error downloading torrent.")

    out = sp.call(["transmission-remote", "-a {0}".format(filename)])
    succ = out.lower().find("success") > 0
    if not succ:
      logger.log(out)
    return succ

  def __init__(self, registrar):
    super(Torrent, self).__init__(registrar)
    self.settings = ConfigParser.SafeConfigParser()
    self.settings.read(utils.get_plugin_settings_paths(__name__))

    registrar.register_service("torrent", self.execute,
      grammar={"name":[], "file": ["file"]},
      usage="""
             USAGE: %s [torrent file | media name | IMDB Link]
             When provided with a .torrent file, it grabs the file and begins
             downloading. With an IMDB link, it extracts the movie name and
             attempts to find the .torrent file closest to what you're looking
             for. A name does the same, except the media name is provided.
            """,
      namespace=__name__)

  def disable(self):
    """Disable all of Torrent's services."""
    self.registrar.unregister_service("torrent", namespace=__name__)

  def execute(self, **kwargs):
    """Download and start the provided media. Downloads the link with the
    highest seed count.

    Keyword arguments:
    file -- the .torrent file to find and download
    name -- either an IMDB link to the media or the media name to search for

    """
    if not self.settings.has_option("Downloads", "download_dir"):
      raise plugin.UnsuccessfulExecution("Could not continue - "
        "no download directory in settings.")

    if "file" in kwargs:
      tfile = kwargs["file"]
      movie_name = "torrent"
    elif "name" in kwargs:
      movie_name = kwargs["name"]
      if movie_name.startswith("http://www.imdb.com/"):
        try:
          response = urllib2.urlopen(movie_name)
          data = response.read()
          match = re.search("<title>(.*?)</title>", data)
          if match:
            title_extra = " - IMDb"
            movie_name = match.group(1)
            if movie_name.endswith(title_extra):
              movie_name = movie_name[0:len(movie_name) - len(title_extra)]
          else:
            return "Error finding IMDB movie title."
        except urllib2.URLError:
          return "Error loading IMDB link."
      tfile = self.search(movie_name)
      if not tfile:
        return "Could not find any torrents."
    else:
      raise plugin.UnsuccessfulExecution("No media name provided.")

    try:
      if self.begin_torrent(tfile):
        return "Now downloading {0}".format(movie_name)
      else:
        return "Torrent downloaded, but could not be started."
    except Exception as err:
      logger.log("Error starting torrent", err)
      raise plugin.UnsuccessfulExecution("Error starting torrent.")

"""if __name__ == "__main__":
  __name__ = "torrent"
  t = torrent()
  #print t.execute("http://www.imdb.com/title/tt1014759/")
  print t.execute("Alice in Wonderland")
  #print t.execute("Alice in Wonderland 2010")
  #print t.execute("http://torrents.thepiratebay.org/5556606/"
  #       "Alice_in_Wonderland_(2010)_DVDRip_XviD-DiAMOND.5556606.TPB.torrent")
  """
