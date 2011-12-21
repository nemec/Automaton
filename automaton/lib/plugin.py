

class UnsuccessfulExecution(Exception):
  """ UnsuccessfulExecution errors are not necessarily fatal.
      All they represent is a failure on the service's part to
      successfully produce normal output. For example, if a
      location service is unable to determine an accurate location,
      it can raise this error to let the calling thread know that
      there is no location available.
  """
  pass


class PluginLoadError(Exception):
  """
  Indicates that the plugin failed to load. If this occurs while
  importing a plugin, that plugin will be disabled.

  """
  pass


class PluginInterface(object):
  """
  Marker class to indicate which class in a plugin's file is the
  actual plugin implementation.
  
  """
  def __init__(self, registrar):
    self.registrar = registrar
