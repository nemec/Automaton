import automaton.lib.plugin


def platform():
  return ['linux', 'mac', 'windows']


class Translate(automaton.lib.plugin.PluginInterface):

  def __init__(self, registrar):
    super(Translate, self).__init__(registrar)
    registrar.register_service("translate", self.execute,
      usage="""
             USAGE: translate lang1 lang2 phrase
             Uses Google to translate the phrase from lang1 to lang2.
             Lang1 and lang2 MUST conform to ISO 639-2 language codes.
             Eg. english -> en, spanish -> es
            """)

  def disable(self):
    self.registrar.unregister_service("translate")

  def execute(self, arg=''):
      from urllib2 import urlopen
      from urllib import urlencode
      import unicodedata

      # The google translate API can be found here:
      # http://code.google.com/apis/ajaxlanguage/documentation/#Examples
      if arg == '' or arg.count(' ') < 2:
        return ''
      lang1 = arg[0:2]
      lang2 = arg[3:5]
      langpair = '{0}|{1}'.format(lang1, lang2)
      text = arg[5:]
      base_url = 'http://ajax.googleapis.com/ajax/services/language/translate?'
      params = urlencode((('v', 1.0),
                       ('q', text),
                       ('langpair', langpair),))
      url = base_url + params
      content = urlopen(url).read()
      start_idx = content.find('"translatedText":"') + 18
      translation = content[start_idx:]
      end_idx = translation.find('"}, "')
      translation = translation[:end_idx]
      return unicodedata.normalize('NFKD',
          unicode(translation, "utf-8")).encode('ascii', 'ignore')
