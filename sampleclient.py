from automaton.lib import exceptions
from automaton.lib.client_wrapper_thrift import ClientWrapper

try:
  client = ClientWrapper(appname="sample")
  client.open()

  try:
    print client.interpret("echo hello")
  except exceptions.ServiceNotProvidedError:
    print "PluginNotLoaded Exception"
  except exceptions.ServiceNotRegisteredError:
    print "Service not registered"
  except exceptions.ClientNotRegisteredError:
    print "Client not registered"
  finally:
    client.close()

except exceptions.ClientError as tx:
  print str(tx)
