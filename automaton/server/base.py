#!/usr/bin/env python

import re
import uuid
import time
import inspect
import threading
from types import GeneratorType
from collections import namedtuple

import automaton.plugins
from automaton.lib import (
  logger, registrar, exceptions, autoplatform, utils,
  clientmanager)
from automaton.lib.plugin import PluginInterface, UnsuccessfulExecution

# pylint: disable-msg=C0103
class AutomatonServer(object):
  """Base class for the Automaton Server."""
  def __init__(self, withgui=False):
    self.withgui = withgui

    self.registrar = registrar.Registrar()

    # A dictionary mapping clientids to registered plugins
    self.client_manager = clientmanager.ClientManager()

    # pylint: disable-msg=C0103
    self.LoadedPlugin = namedtuple('LoadedPlugin', ['obj', 'lock'])
    self.loaded_plugins = {}
    # Update __init__.py in the automaton package when a new plugin is added
    for plugin in automaton.plugins.__all__:
      try:
        self.enablePlugin(plugin)
      except Exception as e:  # pylint: disable-msg=W0703
        logger.log("Error loading module {0}.".format(plugin), e)

  def enablePlugin(self, name):
    """Import and enable a plugin on the server."""
    # Imports the plugin module
    module = __import__('automaton.plugins.{0}'.format(name), fromlist=[name])
    # Either no platform restriction is provided, or the platform is
    # in the restriction set
    if not hasattr(module, 'platform') or (autoplatform.platform in
                                                         module.platform()):
      # Searches through the module for classes that implement the
      # automaton.lib.plugin.PluginInterface class
      # If there is more than one class in a file, only the first is
      # instantiated.
      classes = inspect.getmembers(module,
          lambda obj: inspect.isclass(obj) and
                      issubclass(obj, PluginInterface))
      if len(classes) == 0:
        raise ImportError("No class in {0} implements "
                "automaton.lib.plugins.PluginInterface".format(name))
      cls = classes[0][1](self.registrar)
      self.loaded_plugins[name] = self.LoadedPlugin(cls, threading.Lock())

  def disablePlugin(self, name):
    """Disable a plugin from being available to a user."""
    if name in self.loaded_plugins:
      plugin = self.loaded_plugins[name]
      if hasattr(plugin, "disable"):
        plugin.disable()
      del self.loaded_plugins[name]

  def reloadPlugin(self, name):
    """Disable and re-enable a plugin, reloading the code from source."""
    if name in self.loaded_plugins:
      plugin = self.loaded_plugins[name]
      plugin.lock.acquire()
      try:
        cmd = reload(__import__('automaton.plugins.{0}'.format(name),
                                fromlist=[name]))
        plugin.obj = getattr(cmd, name)()
        logger.log("Plugin {0} has been successfully reloaded.".format(name))
      except Exception as err:
        self.disablePlugin(name)
        logger.log("Exception encountered reloading {0}. "
                  "Plugin disabled.".format(name), err)
        logger.log(name)
      finally:
        plugin.lock.release()

  def get_client(self, clientid, touch_client=True):
    """
    Retrieve the client for the given clientid
    and update its last-accessed time.
    
    Keyword Arguments:
    clientid -- a unique id assigned to the client when registering
    touch_client -- Whether or not to update the last_contact time of
      the client
    
    """
    if clientid not in self.client_manager.registered_clients:
      raise exceptions.ClientNotRegisteredError()
    client = self.client_manager.registered_clients[clientid]
    if touch_client:
      client.last_contact = time.time()
    return client

  def registerClient(self, appname=None, publish_url=None):
    """
    Register a client service with the server. Calculate a UUID that will
    identify which plugins are loaded for each client service and return it
    to the caller.

    """
    ident = str(uuid.uuid1())
    while ident in self.client_manager.registered_clients:
      ident = str(uuid.uuid1())
    if appname is not None:
      ident = re.sub('[\W_]+', '', appname) + '-' + ident
    logger.log("Registering client {0}".format(ident))
    self.client_manager.add_client(ident, publish_url=publish_url)
    return ident

  def unregisterClient(self, clientid):
    """Unregister a client service from the server. Any further use of its
    clientid will result in a ServiceNotRegisteredError.
    
    Arguments:
    clientid -- a unique id assigned to the client when registering

    Raises:
    ClientNotRegisteredError

    """
    if clientid not in self.client_manager.registered_clients:
      raise exceptions.ClientNotRegisteredError()

    logger.log("Unregistering client {0}".format(clientid))
    del self.client_manager.registered_clients[clientid]

  def allowService(self, clientid, name):
    """Register a service for use by a client.

    Arguments:
    clientid -- a unique id assigned to the client when registering
    name -- the name of the service to enable

    Raises:
    ClientNotRegisteredError
    ServiceNotLoadedException

    """
    name = name.lower()
    client = self.get_client(clientid)
    if name not in self.registrar.services:
      raise exceptions.ServiceNotProvidedError(name)

    if name not in client.plugins:
      logger.log("Adding service {0} for client {1}".format(name, clientid))
      client.plugins.add(name)

  def disallowService(self, clientid, name):
    """Unregister a service from being used with a client.

    Arguments:
    clientid -- a unique id assigned to the client when registering
    name -- the name of the service to enable

    Raises:
    ClientNotRegisteredError
    ServiceNotLoadedException

    """
    name = name.lower()
    client = self.get_client(clientid)
    if name not in client.plugins:
      raise exceptions.ServiceNotRegisteredError(name)

    logger.log("Removing service {0} for client {1}".format(name, clientid))
    client.plugins.remove(name)

  def allowAllServices(self, clientid):
    """Allow all services for the given clientid."""
    logger.log("Allowing all services for client {0}".format(clientid))
    self.get_client(clientid).plugins = set(self.registrar.services.keys())

  def disallowAllServices(self, clientid):
    """Disallow all services for the given client id."""
    logger.log("Removing all services for client {0}".format(clientid))
    self.get_client(clientid).plugins = set()

  def interpret(self, clientid, raw):
    """Use the interpreter to translate the raw (arbitrary) text into
    a command:arguments pair that is then executed like normal


    Arguments:
    clientid -- a unique id assigned to the client when registering
    raw -- the raw text to interpret
    
    Raises:
    ClientNotRegisteredError
    ServiceNotRegisteredError
    UnknownIntentError

    """
    client = self.get_client(clientid, touch_client=False)
    with utils.locked(client.lock):
      # TODO put conversation_timeout in settings
      conversation_timeout = 40  # seconds
      if client.last_contact + conversation_timeout < time.time():
        client.current_conversation = None
      client.last_contact = time.time()
      # Continue a previous conversation
      if client.current_conversation is not None:
        try:
          kwargs = {"_raw": raw.lower()}
          output = client.current_conversation.send(kwargs)
        except (StopIteration, AttributeError) as e:
          client.current_conversation = None
      # Start a new conversation
      if client.current_conversation is None:
        matches = self.registrar.find_services(raw)
        
        # remove all unregistered services
        matches = [match for match in matches if 
          match[0] in client.plugins]

        if len(matches) == 0:
          raise exceptions.UnknownIntentError(
            "Execution failed: could not find a registered command.")

        output = None
        # TODO move limit to settings file
        limit = 1  # How many results to try before quitting
        try:
          # Zip terminates with shortest sequence, so stops after
          # matches end or `limit` iterations
          for (ix, (command, namespace, args)) in zip(xrange(limit), matches):
            conversation = self.registrar.request_service(
              svc_name=command, namespace=namespace, argdict=args)
            if conversation:  # Service returns None if it can't handle input
              try:
                output = conversation.next()
                client.current_conversation = conversation
              except AttributeError as e:  # Not a generator, get string output
                output = str(conversation)
                client.history.append(
                  clientmanager.QueryHistory(raw, command, namespace, args))
                client.history.append(
                  clientmanager.ResponseHistory(output))
              break  # We got some good output, don't continue to the next
        except UnsuccessfulExecution as e:
          output = "Execution failed: " + str(e)

      if not output:
        output = "No output."
    
    return output

  def findServices(self, query):
    """Retrieves a list of namespaces and services that match
    the query.
    
    Keyword arguments:
      query -- the search string

    """
    return self.registrar.find_services(query)

  def isService(self, name):
    """Tests if the specified service is provided or not.
    Querying is possible even when unregistered.

    Keyword arguments:
    name -- the name of the service

    """
    return name.lower() in self.registrar.services

  def getAvailableServices(self):
    """Returns a set of strings containing all loaded plugins.
    Querying is possible even when unregistered.

    """
    return self.registrar.services.keys()

  def serviceUsage(self, name):
    """Return the matched services' usage strings.

    Raises:
    ServiceNotProvidedError

    """
    ret = '\n'.join(ns.usage for ns in self.registrar.services[name].values())
    if not ret:
      raise exceptions.ServiceNotProvidedError()
    return ret

  def _start(self):
    """Start the server. Should be implemented in a subclass."""
    pass

  def start(self):
    """Start the server.
    Ensures any networking is done in a separate thread from the UI.

    """
    if self.withgui:
      try:
        import gtk
        import automaton.lib.ui as ui
        ui.StatusIcon(self)
        thread = threading.Thread(target=self._start)
        thread.setDaemon(True)
        thread.start()
        gtk.gdk.threads_init()
        gtk.main()
        return
      except ImportError:
        logger.log("gtk toolkit not present, so no graphical "
                    "user interface will be available.")
    self._start()
