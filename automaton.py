import sys
import Automaton.lib.ClientWrapper as ClientWrapper

try:
  
  client = ClientWrapper.ClientWrapper("localhost")
  client.open()

  try:

    command = sys.argv[1]
    args = ' '.join(sys.argv[2:])

    if client.isScript(command):
      client.registerScript(command)
      print client.execute(command, args)
    else:
      print "Command not found"
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
