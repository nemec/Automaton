import shutil
import os

#@TODO Actually use the Dropbox API
#@TODO Make Windows compatible

import lib.settings_loader as settings_loader

class upload:

  def execute(self, arg = ''):
      if arg == '':
        return help()
      cmd_op = settings_loader.load_script_settings(__name__)
      if not cmd_op.has_key('SYNC_FOLDER'):
        return "No sync folder specified in settings."
      try:
        if os.path.isfile(arg):
          shutil.copy(arg, cmd_op['SYNC_FOLDER'])
        elif os.path.isdir(arg):
          shutil.copytree(arg, cmd_op['SYNC_FOLDER'])
      except shutil.Error, err:
        return "Error with copy: %s" % err
      return "Files uploaded"
      

  def platform(self):
    return ['linux', 'mac', 'windows']

  def help(self):
    return """
            USAGE: upload path_to_file
            Essentially, copies the specified file or folder to a directory that
            is automatically synced with the internet (eg. Dropbox)
           """

