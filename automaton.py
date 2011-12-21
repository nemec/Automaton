import sys
import automaton.client.thrift as thrift_client
import automaton.lib.exceptions as exceptions

try:
  client = thrift_client.ClientWrapper("localhost", appname="cmd")
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

except exceptions.ClientException as tx:
  print repr(tx.message)
