from urllib2 import urlopen, URLError
from urllib import urlencode
import unicodedata

import automaton.lib.plugin


def platform():
  return ['linux', 'mac', 'windows']


class Translate(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Translate, self).__init__(registrar)
    registrar.register_service("translate", self.execute,
      grammar={
        "text": [],
        "from": ["from"],
        "to": ["to"],
      },
      usage="""
             USAGE: translate lang1 lang2 phrase
             Uses Google to translate the phrase from lang1 to lang2.
             Lang1 and lang2 MUST conform to ISO 639-2 language codes.
             Eg. english -> en, spanish -> es
            """)

  def disable(self):
    self.registrar.unregister_service("translate")

  def execute(self, arg='', **kwargs):
      # The google translate API can be found here:
      # http://code.google.com/apis/ajaxlanguage/documentation/#Examples
      lang1 = kwargs["from"]
      lang2 = kwargs["to"]
      langpair = '{0}|{1}'.format(lang1, lang2)
      text = kwargs["text"]
      
      base_url = 'http://ajax.googleapis.com/ajax/services/language/translate?'
      params = urlencode((('v', 1.0),
                       ('q', text),
                       ('langpair', langpair),))
      url = base_url + params
      try:
        content = urlopen(url).read()
      except URLError:
        return "Could not contact translation server."
      start_idx = content.find('"translatedText":"') + 18
      translation = content[start_idx:]
      end_idx = translation.find('"}, "')
      translation = translation[:end_idx]
      return unicodedata.normalize('NFKD',
          unicode(translation, "utf-8")).encode('ascii', 'ignore')
