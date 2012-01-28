import sys
import automaton.client.rest as client_lib
import automaton.lib.exceptions as exceptions

try:
  client = client_lib.ClientWrapper("localhost", appname="cmd")
  client.open()

  try:
    client.allowAllServices()
    
    cmd = ' '.join(sys.argv[1:])
    if cmd == "help":
      print client.getAvailableServices()
    else:
      print client.interpret(cmd)
  except exceptions.ClientNotRegisteredError:
    print "Service not registered"
  except exceptions.ServiceNotProvidedError as e:
    print e
  except exceptions.ServiceNotRegisteredError as e:
    print e
  except exceptions.UnknownIntentError:
    print "Cannot understand query."
  finally:
    client.close()

except exceptions.ClientError as tx:
  print repr(tx)
