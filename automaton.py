import sys
import Automaton.lib.ClientWrapper as ClientWrapper

try:
  
  client = ClientWrapper.ClientWrapper("localhost", appname="cmd")
  client.open()

  try:
    client.allowAllServices()
    print client.interpret(' '.join(sys.argv[1:]))
  except ClientWrapper.ClientNotRegisteredError:
    print "Service not registered"
  except ClientWrapper.ServiceNotProvidedError as e:
    print e
  except ClientWrapper.ServiceNotRegisteredError as e:
    print e
  finally:
    client.close()

except ClientWrapper.ClientException as tx:
  print repr(tx.message)
