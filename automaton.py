import sys
import automaton.client.thrift as thrift_client

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
