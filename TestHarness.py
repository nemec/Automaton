import re
import threading
import time

import Automaton.lib.exceptions as exceptions

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
        "google": [("hello world",  "A Hello world program is a computer.+")],
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

tests = ["google", "exe", "gettime", "echo", "google", "latitude", "mail", "map",
         "weather", "wiki", "say"]

def test_client(client):
  success = set()
  failure = {}

  for key in test_data:
    if key in tests:
      print "testing {0}...".format(key)
      try:
        if client.isService(key):
          client.allowService(key)
          for test in test_data[key]:
            resp = client.interpret(" ".join([key, test[0]])).strip()
            match = re.match(test[1] + "$", resp, flags=re.DOTALL)
            if match and key not in failure:
              success.add(key)
            else:
              failure[key] = "expected \"{0}\", got \"{1}\"".format(test[1], resp)
              success.discard(key)
              break
        else:
          failure[key] = "not loaded."

        try:
          text = client.serviceUsage(key)
          if len(text) == 0:
            failure[key + "-help"] = "Help is empty."
        except AttributeError:
          if "help" not in failure:
            failure["help"] = "client.serviceUsage cannot be found"
        
      except Exception as e:
        failure[key] = "encountered exception during execution: " + e
        success.discard(key)

  if len(success) > 0:
    print "Successful execution for:"
    for script in success:
      print " ", script

  if len(failure) > 0:
    print
    print "Failed execution for:"
    for key in failure:
      print " ", key, ":", failure[key]


def test_server():
  from Automaton.lib.AutomatonServer_pyro import PyroServer
  import Automaton.lib.ClientWrapper_pyro as ClientWrapper_pyro

  print "Starting test server"

  server = PyroServer(port = 9090)
  server.initialize()

  thread = threading.Thread(target=server.start)
  thread.daemon = True
  thread.start()
  time.sleep(3) # wait for server to initialize

  success = set()
  failure = {}

  try:
    client = ClientWrapper_pyro.ClientWrapper(appname="testharness",port=9090)

    test = "interpreting without registering"
    try:
      client.interpret("echo hello")
      failure[test] = "Requesting service should fail."
    except exceptions.ClientNotRegisteredError:
      success.add(test)
    client.open()

    print "Starting server Testing..."

    test = "serviceNotProvidedError"
    try:
      try:
        client.allowService("asdkjhasdkjh")
        failure[test] = "somehow registered service with random name..."
      except exceptions.ServiceNotProvidedError:
        success.add(test)
    except Exception as e:
      failure[test] = "Unknown exception encountered: " + e

    test = "allowAllServices"
    try:
      client.allowAllServices()
      try:
        client.interpret("echo hello")
        success.add(test)
      except exceptions.ServiceNotRegisteredError:
        failure[test] = "allowAllServices did not enable echo service"
    except Exception as e:
      failure[test] = "Unknown exception encountered: " + e

    test = "disallowService"
    try:
      client.disallowService("echo")
      try:
        client.interpret("echo hello")
        failure[test] = "disallowService did not disable echo service"
      except exceptions.ServiceNotRegisteredError:
        success.add(test)
    except Exception as e:
      failure[test] = "Unknown exception encountered: " + e

    test = "allowService"
    try:
      client.allowService("echo")
      try:
        client.interpret("echo hello")
        success.add(test)
      except exceptions.ServiceNotRegisteredError:
        failure[test] = "allowService did not enable echo service"
    except Exception as e:
      failure[test] = "Unknown exception encountered: " + e
    
    test = "isService"
    try:
      if client.isService("echo"):
        success.add(test)
      else:
        failure[test] = "Failed to determine echo as a service"
    except Exception as e:
      failure[test] = "Unknown exception encountered: " + e

    test = "getAvailableServices"
    try:
      if len(client.getAvailableServices()) > 0:
        success.add(test)
      else:
        failure[test] = "No available services"
    except Exception as e:
      failure[test] = "Unknown exception encountered: " + e


    if len(success) > 0:
      print "Successful execution for:"
      for script in success:
        print " ", script

    if len(failure) > 0:
      print
      print "Failed execution for:"
      for key in failure:
        print " ", key, ":", failure[key]

    client.close()

  except ClientWrapper_pyro.ClientException as tx:
    print 'Client exception encountered: ' + tx.message

  server.daemon.shutdown()


def test_pyro():
  from Automaton.lib.AutomatonServer_pyro import PyroServer
  import Automaton.lib.ClientWrapper_pyro as ClientWrapper_pyro

  print "Starting Pyro Server"

  server = PyroServer(port = 9092)
  server.initialize()

  thread = threading.Thread(target=server.start)
  thread.daemon = True
  thread.start()
  time.sleep(3) # wait for server to initialize

  try:
    client = ClientWrapper_pyro.ClientWrapper(appname="testharness",port=9092)
    client.open()

    print "Starting Pyro Testing..."

    test_client(client)

    client.close()

  except ClientWrapper_pyro.ClientException as tx:
    print 'Client exception encountered: ' + tx.message

  server.daemon.shutdown()


def test_thrift():
  from Automaton.lib.AutomatonServer_thrift import ThriftServer
  import Automaton.lib.ClientWrapper as ClientWrapper_thrift

  print "Starting Thrift Server"

  server = ThriftServer(port = 9091)
  server.initialize()

  thread = threading.Thread(target=server.start)
  thread.daemon = True
  thread.start()
  time.sleep(3) # wait for server to initialize

  try:
    client = ClientWrapper_thrift.ClientWrapper(appname="testharness",port=9091)
    client.open()

    print "Starting Thrift Testing..."

    test_client(client)

    client.close()

  except ClientWrapper_thrift.ClientException as tx:
    print 'Client exception encountered: ' + tx.message


if __name__ == "__main__":
  test_server()
  test_pyro()
  #test_thrift()
