import sys
import automaton.client.thrift as thrift_client
import automaton.lib.exceptions as exceptions

try:
  client = thrift_client.ClientWrapper("localhost", appname="cmd")
  client.open()

  try:
    client.allowAllServices()

    while True:
      cmd = raw_input("> ")
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
  print repr(tx.message)
except KeyboardInterrupt:
  pass
