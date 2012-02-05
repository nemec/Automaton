try:
  import unittest2 as unittest
except ImportError:
  import unittest
import re
import os
import datetime
import threading
from io import StringIO

import automaton
from automaton.lib import autoplatform, utils


class TestAutoPlatform(unittest.TestCase):

  def test_dirs(self):
    if autoplatform.platform == "windows":
      self.assertNotRaises(autoplatform.personaldir(), KeyError)
      self.assertNotRaises(autoplatform.systemdir(), KeyError)
    elif autoplatform.platform in ("linux", "mac"):
      personal = autoplatform.personaldir()
      self.assertTrue(personal.endswith(".automaton/") and
                        not os.path.isfile(personal))
      self.assertEqual(autoplatform.systemdir(), "/etc/automaton/")
    else:
      raise Exception("System platform not in accepted list of platforms.")

    self.assertTrue(os.path.isdir(autoplatform.localdir()))
    self.assertIsNone(
      autoplatform.get_existing_file(r"__\/|illegal", strict=True))
    self.assertIsNotNone(
      autoplatform.get_existing_file(r"__\/|illegal", strict=False))


class TestUtils(unittest.TestCase):

  def test_threading(self):
    stream_lock = threading.Lock()
    iostream = StringIO()
    output_length = 1000
    def testfunc(lock, stream):
      with utils.locked(lock):
        for x in xrange(output_length):
          stream.write(unicode(x))

    first = utils.spawn_thread(testfunc, stream_lock, iostream)
    second = utils.spawn_thread(testfunc, stream_lock, iostream)
    first.join()
    second.join()
    test_output = u''.join(unicode(x) for x in
                            range(output_length) + range(output_length))
    self.assertEqual(test_output, iostream.getvalue())

  def test_module_name(self):
    self.assertEqual(utils.get_module_name('/home/user/AIM.py'), 'AIM')
    self.assertEqual(utils.get_module_name('/home/user/AIM'), 'AIM')
    self.assertEqual(utils.get_module_name('/home/user/automaton.lib'), 'lib')

  def test_settings_paths(self):
    self.assertTrue(any(os.path.isdir(os.path.dirname(fil))
      for fil in utils.get_app_settings_paths("module")))
    self.assertTrue(any(os.path.isdir(os.path.dirname(fil))
      for fil in utils.get_plugin_settings_paths("module")))

  def test_humanize_join(self):
    seq = ['1', '2', '3', '4']
    separator = '[_]'
    spacing = '>'
    output = utils.humanize_join(seq, separator=separator, conjunction='and',
      oxford_comma=False)
    self.assertEqual('1[_] 2[_] 3 and 4', output)

    output = utils.humanize_join(seq, separator=separator, conjunction='and',
      oxford_comma=True)
    self.assertEqual('1[_] 2[_] 3[_] and 4', output)
    
    output = utils.humanize_join(seq, separator=separator, conjunction='or',
      oxford_comma=True)
    self.assertEqual('1[_] 2[_] 3[_] or 4', output)
    
    separator = '-'
    
    output = utils.humanize_join(seq, separator=separator, spacing=spacing,
      conjunction='or', oxford_comma=True)
    self.assertEqual('1->2->3->or>4', output)

  def test_text_to_int(self):
    self.assertEqual([utils.text_to_int(word) for word in
      ["one", "two", "three", "four", "five", "six", "seven", "eight",
      "nine", "ten", "fifteen", "eighteen", "twenty", "twenty five",
      "ten and a quarter", "fifteen and a half",
      "thirty five and three-quarters"]],
      [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 18, 20, 25, 10.25, 15.5, 35.75])


  def text_to_absolute_time(self):
    import time
    dtime = datetime.today()
    
    self.assertEquals(utils.text_to_absolute_time("3:32:08 AM"),
      datetime.replace(hour=3, minute=32, second=8))
    self.assertEquals(utils.text_to_absolute_time("3:32:08 p.m."),
      datetime.replace(hour=15, minute=32, second=8))
    self.assertEquals(utils.text_to_absolute_time("5:34 pm"),
      datetime.replace(hour=17, minute=34, second=0))


if __name__ == "__main__":
  unittest.main()
