import sys
import Automaton.lib.ClientWrapper as ClientWrapper

try:
  
  client = ClientWrapper.ClientWrapper("localhost", appname="cmd")
  client.open()

  try:
    command = sys.argv[1]
    args = ' '.join(sys.argv[2:])
    
    if command == '-i':
      [client.registerPlugin(x) for x in client.getAvailablePlugins()]
      print client.interpret(args)
    elif client.isPlugin(command):
      client.registerPlugin(command)
      print client.execute(command, args)
    else:
      print "Command not found"
  except ClientWrapper.ServiceNotRegisteredException:
    print "Service not registered"
  except ClientWrapper.PluginNotLoadedException, e:
    print e
  except ClientWrapper.PluginNotRegisteredException, e:
    print e
  finally:
    client.close()

except ClientWrapper.ThriftException, tx:
  print repr(tx.message)
