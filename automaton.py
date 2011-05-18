import sys
import automaton.client.thrift as thrift_client

try:
  
  client = thrift_client.ClientWrapper("localhost", appname="cmd")
  client.open()

  try:
    client.allowAllServices()
    print client.interpret(' '.join(sys.argv[1:]))
  except thrift_client.ClientNotRegisteredError:
    print "Service not registered"
  except thrift_client.ServiceNotProvidedError as e:
    print e
  except thrift_client.ServiceNotRegisteredError as e:
    print e
  finally:
    client.close()

except thrift_client.ClientException as tx:
  print repr(tx.message)
