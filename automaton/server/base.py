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
  logger, registrar, exceptions,autoplatform, input_sanitizer, utils)
from automaton.lib.clientmanager import ClientManager
from automaton.lib.plugin import PluginInterface, UnsuccessfulExecution

# pylint: disable-msg=C0103
class AutomatonServer(object):
  """Base class for the Automaton Server."""
  def __init__(self, withgui=False):
    self.needsgui = withgui

    self.registrar = registrar.Registrar()
    self.sanitizer = input_sanitizer.InputSanitizer(self.registrar)

    # A dictionary mapping clientids to registered plugins
    self.client_manager = ClientManager()

    # pylint: disable-msg=C0103
    self.LoadedPlugin = namedtuple('LoadedPlugin', ['obj', 'lock'])
    self.loaded_plugins = {}
    # Update __init__.py in the automaton package when a new plugin is added
    for plugin in automaton.plugins.__all__:
      try:
        self.enablePlugin(plugin)
      except Exception as e:
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

  def get_client(self, clientid):
    if clientid not in self.client_manager.registered_clients:
      raise exceptions.ClientNotRegisteredError()
    client = self.client_manager.registered_clients[clientid]
    client.last_contact = time.time()
    return client

  def registerClient(self, appname=None):
    """Register a client service with the server. Calculate a UUID that will
    identify which plugins are loaded for each client service and return it
    to the caller.

    """
    ident = str(uuid.uuid1())
    while ident in self.client_manager.registered_clients:
      ident = str(uuid.uuid1())
    if appname is not None:
      ident = re.sub('[\W_]+', '', appname) + '-' + ident
    logger.log("Registering client {0}".format(ident))
    self.client_manager.add_client(ident)
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
    self.get_client(clientid).plugins = set(
                                              self.registrar.services.keys())

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
    client = self.get_client(clientid)
    with utils.locked(client.lock):
      # Continue a previous conversation
      if client.current_conversation is not None:
        try:
          kwargs = {"_raw": raw.lower()}
          output = client.current_conversation.send(kwargs)
        except StopIteration:
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
        limit = 1  # How many results to try before quitting
        try:
          for (ix, (command, namespace, args)) in enumerate(matches):
            if ix == limit:
              break
            #args = self.sanitizer.alias(args)
            #args = self.sanitizer.sanitize(args)
            output = self.registrar.request_service(
              svc_name=command, namespace=namespace, argdict=args)
            if output:
              if isinstance(output, GeneratorType):
                client.current_conversation = output
                output = output.next()
              else:
                client.history.append((command, args))
              break  # We got some good output, don't continue to the next
        except UnsuccessfulExecution as e:
          output = "Execution failed: " + str(e)

      if output:
        self.sanitizer.set_prev_alias(output)
      else:
        output = "No output."
    
    return output

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


  """ Start server initialization functions """
  def start(self):
    """Start the server.
    Ensures any networking is done in a separate thread from the UI.

    """
    if hasattr(self, "_start"):
      # Spawn a second thread for the _start method
      if self.needsgui:
        thread = threading.Thread(target=self._start)
        thread.setDaemon(True)
        thread.start()
        self.load_gui()
      else:
        self._start()

  def load_gui(self):
    """Load the UI."""
    try:
      import gtk
    except ImportError:
      logger.log("gtk toolkit not present, so no graphical "
                  "user interface will be available.")
    import automaton.lib.ui as ui
    ui.StatusIcon(self)
    gtk.gdk.threads_init()
    gtk.main()
