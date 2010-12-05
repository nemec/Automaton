import sys
import Automaton.lib.ClientWrapper as ClientWrapper

try:
  
  client = ClientWrapper.ClientWrapper("localhost")
  client.open()

  try:
    command = sys.argv[1]
    args = ' '.join(sys.argv[2:])
    
    if command == '-i':
      [client.registerScript(x) for x in client.getAvailableScripts()]
      client.interpret(args)
    elif client.isScript(command):
      client.registerScript(command)
      print client.execute(command, args)
    else:
      print "Command not found"
  except ClientWrapper.ServiceNotRegisteredException:
    print "Service not registered"
  except ClientWrapper.ScriptNotLoadedException, e:
    print e
  except ClientWrapper.ScriptNotRegisteredException, e:
    print e
  finally:
    client.close()

except ClientWrapper.ThriftException, tx:
  print repr(tx.message)
