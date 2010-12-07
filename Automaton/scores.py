class scores:

  def execute(self, arg = ''):
    import urllib
    from BeautifulSoup import BeautifulSoup as bs
    import re
    import datetime
    
    date = datetime.date.today().strftime("%Y%m%d")
    html = urllib.urlopen("http://mobileapp.espn.go.com/ncb/scoreboard?date=" + date + "&groupId=8").read()
    soup = bs(html)
    al = soup.findAll('div',attrs={'class': re.compile("ind(\salt)?$"), 'style': re.compile("white-space: nowrap;")})
    ret=''
    for line in al:
      ret = ret + re.sub(r'<[^>]*?>', '', str(line)) + '\n'
    if ret == '':
      ret = "No games"
    return ret.strip()

  def platform(self):
    return ['linux','mac','windows']

  def help(self):
    return """
            USAGE: scores
            Gets the latest A&M basketball scores from the espn mobile website.
           """

