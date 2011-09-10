import re
import urllib
import urllib2
import os.path
import subprocess as sp
from BeautifulSoup import BeautifulSoup

import automaton.lib.plugin as plugin
import automaton.lib.logger as logger
import automaton.lib.settings_loader as settings_loader


class Torrent(plugin.PluginInterface):

  search_urls = {
    "pirate_bay": "http://thepiratebay.org/search.php?q=",
  }

  def search(self, name):
    results = []
    for url in self.search_urls.values():
      try:
        page = urllib.urlopen(url + name).read()
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
      except Exception as e:
        print e
        continue

      top = None

      try:
        top = max(results)[1]
      except ValueError:
        pass

      return top

  def begin_torrent(self, movie_name):
    filename = os.path.join(self.cmd_op["DOWNLOAD_DIR"],
                                                  os.path.basename(movie_name))
    try:
      urllib.urlretrieve(movie_name, filename)
    except Exception as e:
      logger.log("Error downloading torrent:", e)
      raise Exception("Error downloading torrent.")

    out = sp.call(["transmission-remote", "-a {0}".format(filename)])
    succ = out.lower().find("success") > 0
    if not succ:
      logger.log(out)
    return succ

  def __init__(self, registrar):
    super(Torrent, self).__init__(registrar)
    self.cmd_op = settings_loader.load_plugin_settings(__name__)

    registrar.register_service("torrent", self.execute,
      usage="""
             USAGE: torrent [torrent file | media name | IMDB Link]
             When provided with a .torrent file, it grabs the file and begins
             downloading. With an IMDB link, it extracts the movie name and
             attempts to find the .torrent file closest to what you're looking
             for. A name does the same, except the media name is provided.
            """)

  def disable(self):
    self.registrar.unregister_service("torrent")

  def execute(self, arg=''):
    movie_name = arg

    if "DOWNLOAD_DIR" not in self.cmd_op:
      return "Could not continue - no download directory in settings."

    if movie_name.endswith(".torrent"):
      tfile = movie_name
      movie_name = "torrent"
    else:
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
        except urllib2.URLError as e:
          return "Error loading IMDB link."
      tfile = self.search(movie_name)
      if not tfile:
        return "Could not find any torrents."
      self.begin_torrent(tfile)

    try:
      if self.begin_torrent(tfile):
        return "Now downloading {0}".format(movie_name)
      else:
        return "Torrent downloaded, but could not be started."
    except Exception as e:
      logger.log("Error starting torrent", e)
      return "Error starting torrent."

  def grammar(self):
    return ("torrent{\n"
              "keywords = torrent\n"
              "arguments = *\n"
            "}")


if __name__ == "__main__":
  __name__ = "torrent"
  t = torrent()
  #print t.execute("http://www.imdb.com/title/tt1014759/")
  print t.execute("Alice in Wonderland")
  #print t.execute("Alice in Wonderland 2010")
  #print t.execute("http://torrents.thepiratebay.org/5556606/"
  #       "Alice_in_Wonderland_(2010)_DVDRip_XviD-DiAMOND.5556606.TPB.torrent")
