import ClientWrapper

try:
  
  client = ClientWrapper.ClientWrapper()
  client.open()

  try:
    print client.getAvailableScripts()
    if client.isScript("echo"):
      client.registerScript("echo")
      print client.execute("echo", "hello")
      client.unregisterScript("echo")
  except ClientWrapper.ScriptNotLoadedException:
    print "ScriptNotLoaded Exception"
  except ClientWrapper.ServiceNotRegisteredException:
    print "Service not registered"
  except ClientWrapper.ScriptNotRegisteredException:
    print "Script not registered"
  finally:
    client.close()

except ClientWrapper.ThriftException, tx:
  print '%s' % (tx.message)
