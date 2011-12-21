from urllib2 import urlopen, URLError
from urllib import urlencode
import unicodedata

import automaton.lib.plugin

# pylint: disable-msg=W0101
raise automaton.lib.plugin.PluginLoadError(
  "Translations from google are now a paid service, this plugin must "
  "be rewritten to use their new API keys.")


def platform():
  """Return the list of platforms the plugin is available for."""
  return ['linux', 'mac', 'windows']


class Translate(automaton.lib.plugin.PluginInterface):
  """Translate text from one language to another by name or language code."""
  language_codes = {
    "afrikaans": "af",
    "albanian": "sq",
    "arabic": "ar",
    "belarusian": "be",
    "bulgarian": "bg",
    "catalan": "ca",
    "chinese simplified": "zh-CN",
    "chinese traditional": "zh-TW",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "estonian": "et",
    "filipino": "tl",
    "finnish": "fi",
    "french": "fr",
    "galician": "gl",
    "german": "de",
    "greek": "el",
    "hebrew": "iw",
    "hindi": "hi",
    "hungarian": "hu",
    "icelandic": "is",
    "indonesian": "id",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "latvian": "lv",
    "lithuanian": "lt",
    "macedonian": "mk",
    "malay": "ms",
    "maltese": "mt",
    "norwegian": "no",
    "persian": "fa",
    "polish": "pl",
    "portuguese": "pt",
    "romanian": "ro",
    "russian": "ru",
    "serbian": "sr",
    "slovak": "sk",
    "slovenian": "sl",
    "spanish": "es",
    "swahili": "sw",
    "swedish": "sv",
    "thai": "th",
    "turkish": "tr",
    "ukrainian": "uk",
    "vietnamese": "vi",
    "welsh": "cy",
    "yiddish": "yi"
  }

  def __init__(self, registrar):
    super(Translate, self).__init__(registrar)
    registrar.register_service("translate", self.execute,
      grammar={
        "text": [],
        "from": ["from"],
        "to": ["to"],
      },
      namespace=__name__)

  def disable(self):
    """Disable all of Translate's services."""
    self.registrar.unregister_service("translate", namespace=__name__)

  def execute(self, **kwargs):
    """Translate text from one language to another. The text is normalized
    to ascii before being returned.

    Keyword arguments:
    from -- source language, either the language name or the language code
    to -- destination language, either the name or language code
    text -- the text to translate

    """
    # The google translate API can be found here:
    # http://code.google.com/apis/ajaxlanguage/documentation/#Examples
    if "to" not in kwargs:
      return "Please provide a destination language."
    if "from" not in kwargs:
      return "Please provide the language of the message."

    lang1 = self.language_codes.get(kwargs["from"].lower(), kwargs["from"])
    lang2 = self.language_codes.get(kwargs["from"].lower(), kwargs["from"])
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
