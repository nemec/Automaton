try:
  import unittest2 as unittest
except ImportError:
  import unittest

loader = unittest.TestLoader()
test_suite = loader.discover(
  "automaton.plugins", pattern="weather.py", top_level_dir='..')

if __name__ == "__main__":
  runner = unittest.runner.TextTestRunner()
  runner.run(test_suite)
