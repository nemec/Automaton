import re
import Automaton.lib.ClientWrapper as ClientWrapper_thrift
import Automaton.lib.ClientWrapper_pyro as ClientWrapper_pyro

# Format:
#  key: scriptname, value: list of tuples to check
#  tuple[0]: argument string
#  tuple[1]: expected response (as regexp or straight string)

def notmatch(s):
  return "^((?!%s).)*$" % s

test_data ={"echo": [("hello", "hello")],
        "exe": [("echo hello", "hello")],
        "gettime": [("",   "\d{1,2}:\d{1,2} (A|P)M"),
                    ("24", "\d{1,2}:\d{1,2}")],
        "google": [("hello world",  "A Hello World program is a computer "
                                    "program which prints out Hello World "
                                    "on   a display device. It is used in "
                                    "many introductory tutorials for teaching "
                                    "a ...")],
        "latitude": [("", notmatch("Error")),
                    ("noreverse", "\(-?\d+(\.\d+)?, -?\d+(\.\d+)?\)")],
        "mail": [("", notmatch("Error"))],
        "map": [("college station, texas to houston, texas",
                          notmatch("malformed"))],
        "memo": [("testing success", "Inserted into memo file.")],
        "music": [("play", notmatch("Error"))],
        "pandora": [("g", notmatch("Error"))],
        "say": [("This is a test of Automaton text to speech", "")],
        "schedule": [("echo done! in ten and a half seconds",   "Command scheduled."),
                     ("echo first in one second",   "Command scheduled."),
                     ("echo absolute at 10:05pm",   "Command scheduled."),
                     ("echo absolute at 5:00 A.M.",   "Command scheduled."),
                     ("echo absolute at 5:00:4 AM",   "Command scheduled."),
                     ("echo absolute at 5:55",   "Command scheduled.")],
        "weather": [("", "(There is no weather data for this location)|"
                            "(The weather.+)"),
                    ("Houston,tx", "(There is no weather data for this location)|"
                            "(The weather.+)"),
                    ("last", "Data for.+")],
        "wiki": [("hello", "\"Hello is a salutation or greeting.+")],
       }

tests = ["exe", "gettime", "echo", "google", "latitude", "mail", "map",
         "memo", "say", "weather", "wiki"]

success = set()
failed = {}

try:
  
  cthrift = ClientWrapper_thrift.ClientWrapper()
  cthrift.open()

  for key in test_data:
    if key in tests:
      print "testing %s..." % key
      try:
        if cthrift.isScript(key):
          cthrift.registerScript(key)
          for test in test_data[key]:
            resp = cthrift.execute(key, test[0]).strip()
            match = re.match(test[1] + "$", resp, flags=re.DOTALL)
            if match and key not in failed:
              success.add(key)
            else:
              failed[key] = "expected \"%s\", got \"%s\"" % (test[1], resp)
              success.discard(key)
              break
        else:
          failed[key] = "not loaded."
      except Exception, e:
        failed[key] = "encountered exception during execution: %s" % e
        success.remove(key)

  cthrift.close()
except ClientWrapper_thrift.ThriftException, tx:
  print '%s' % (tx.message)

if len(success) > 0:
  print "Successful execution for:"
  for script in success:
    print script

if len(failed) > 0:
  print
  print "Failed execution for:"
  for key in failed:
    print key, failed[key]
