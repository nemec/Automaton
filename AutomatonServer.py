#!/usr/bin/env python

import sys
sys.path.append('/home/dan/prg/Automaton/gen-py')
sys.path.append('/home/dan/prg/Automaton/Automaton')

from automaton_thrift import Script
from automaton_thrift.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import uuid

import Automaton
from Automaton import *
import Automaton.lib.logger as logger

class AutomatonServer:
  def __init__(self):
    # A dictionary mapping serviceids to registered scripts
    self.registeredServices = {}
    # Update __init__.py in the Automaton package when a new script is added
    self.loadedScripts = set()
    for script in Automaton.__all__:
      try:
        if getPlatform() in globals()[script].platform():
          self.loadedScripts.add(script)
      except (AttributeError, TypeError):
        self.loadedScripts.add(script)

  # Registers a client service with the server. Calculates a UUID that will
  # identify which scripts are loaded for each client service
  # Arguments: none
  # Return value: string
  # Throws: none
  def registerService(self):
    id = str(uuid.uuid1())
    while self.registeredServices.has_key(id):
      print id
      id = str(uuid.uuid1())
    logger.log("Registering service %s" % id)
    self.registeredServices[id]=set()
    return id

  # Unregisters a client service from the server. Any further use of its serviceid will
  # result in a ServiceNotRegisteredException
  # Arguments: serviceid:string - id associated with a registered service
  # Return value: void
  # Throws: ServiceNotRegisteredException
  def unregisterService(self, serviceid):
    if serviceid not in self.registeredServices:
      raise ServiceNotRegisteredException()

    logger.log("Unregistering service %s" % serviceid)
    del self.registeredServices[serviceid]
    return

  # Registers a script for use by a client service.
  # Arguments: serviceid:string, scriptname:string
  # Return value: void
  # Throws: ServiceNotRegisteredException, ScriptNotLoadedException
  def registerScript(self, serviceid, scriptname): #void
    if serviceid not in self.registeredServices:
      raise ServiceNotRegisteredException()
    if scriptname not in self.loadedScripts:
      raise ScriptNotLoadedException()

    if scriptname not in self.registeredServices[serviceid]:
      logger.log("Adding script %s for service %s" % (scriptname, serviceid))
      self.registeredServices[serviceid].add(scriptname)
    return

  # Unregisters a script from a client service.
  # Arguments: serviceid:string, scriptname:string
  # Return value: void
  # Throws: ServiceNotRegisteredException, ScriptNotLoadedException
  def unregisterScript(self, serviceid, scriptname): #void
    if serviceid not in self.registeredServices:
      raise ServiceNotRegisteredException()
    if scriptname not in self.registeredServices[serviceid]:
      raise ScriptNotRegisteredException()

    logger.log("Removing script %s for service %s" % (scriptname, serviceid))
    self.registeredServices[serviceid].remove(scriptname)
    return

  # Executes the provided script with any associated arguments.
  # Arguments: serviceid:string, scriptname:string, arguments:string
  # Return value: void
  # Throws: ServiceNotRegisteredException, ScriptNotRegisteredException
  def execute(self, serviceid, scriptname, arguments): #string
    if serviceid not in self.registeredServices:
      raise ServiceNotRegisteredException()
    if scriptname not in self.registeredServices[serviceid]:
      raise ScriptNotRegisteredException()

    # Executes module from the pool of globally imported modules.
    # Safe because only legal scripts are allowed to be registered.
    return globals()[scriptname].execute(arguments)

  # Tests if the specified script is loaded or not.
  # Querying is possible even when unregistered
  # Arguments: scriptname:string
  # Return value: bool
  # Throws: none
  def isScript(self, scriptname):
    return scriptname in self.loadedScripts

  # Returns a set of strings containing all loaded scripts
  # Querying is possible even when unregistered
  # Arguments: none
  # Return value: set<string>
  # Throws: none
  def getAvailableScripts(self): #set<string>
    return self.loadedScripts

  # Returns the contents of the specified script's help() method
  # Replaces the complicated help "command"
  # Arguments: scriptname:string
  # Return value: string
  # Throws ScriptNotLoadedException
  def scriptUsage(self, scriptname):
    if scriptname not in self.loadedScripts:
      raise ScriptNotLoadedException()
    return globals()[scriptname].help()

def getPlatform():
  if sys.platform.startswith('win'):
    return 'windows'
  elif sys.platform.startswith('darwin'):
    return 'mac'
  else:
    return 'linux'

handler = AutomatonServer()
processor = Script.Processor(handler)
transport = TSocket.TServerSocket(9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

#Threaded server allows for multiple connections
server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)

print 'Starting the server...'
try:
  server.serve()
except KeyboardInterrupt:
  pass

