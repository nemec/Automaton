import sys
import automaton.client.rest as client_lib
import automaton.lib.exceptions as exceptions

try:
  client = client_lib.ClientWrapper("localhost", appname="cmd")
  client.open()

  try:
    client.allowAllServices()
    
    cmd = ''
    if len(sys.argv) > 1:
      cmd = ' '.join(sys.argv[1:])

    while True:
      if cmd == "help":
        print client.getAvailableServices()
      elif cmd != '':
        try:
          print client.interpret(cmd)
        except exceptions.ServiceNotProvidedError as err:
          print err
        except exceptions.ServiceNotRegisteredError as err:
          print err
        except exceptions.UnknownIntentError:
          print "Cannot understand query."
      cmd = raw_input("> ")
  except exceptions.ClientNotRegisteredError:
    print "Service not registered"
  finally:
    try:
      client.close()
    except exceptions.ClientNotRegisteredError:
      pass

except exceptions.ClientError as err:
  print repr(err)
except (KeyboardInterrupt, EOFError):
  pass
