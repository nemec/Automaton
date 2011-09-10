from automaton.lib.client_wrapper_thrift import ClientWrapper

try:
  client = ClientWrapper(appname="sample")
  client.open()

  try:
    print client.getAvailablePlugins()
    if client.isPlugin("echo"):
      client.registerPlugin("echo")
      print client.execute("echo", "Successful execution")
      print client.interpret("can you repeat how are you please")
      client.unregisterPlugin("echo")
  except ClientWrapper.PluginNotLoadedException:
    print "PluginNotLoaded Exception"
  except ClientWrapper.ServiceNotRegisteredException:
    print "Service not registered"
  except ClientWrapper.PluginNotRegisteredException:
    print "Plugin not registered"
  finally:
    client.close()

except ClientWrapper.ThriftException as tx:
  print str(tx.message)
