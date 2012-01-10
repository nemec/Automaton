import gtk
import threading

from automaton.lib import exceptions
from automaton.lib.utils import locked
from automaton.lib.plugin import UnsuccessfulExecution


class StatusIcon(gtk.StatusIcon):
  """Icon that displays itself in the status bar and gives access
  to Automaton.

  """
  def __init__(self, server):
    gtk.StatusIcon.__init__(self)
    self.server = server
    self.window = None
    menu = '''
            <ui>
              <menubar name="Menubar">
                <menu action="Menu">
                  <menuitem action="Reload"/>
                  <menuitem action="Registrar"/>
                  <separator/>
                  <menuitem action="About"/>
                  <menuitem action="Quit"/>
                </menu>
              </menubar>
            </ui>
          '''
    actions = [
      ('Menu', None, 'Menu'),
      ('Reload', None, 'Reload'),
      ('Registrar', None, 'Show Registrar Data', None, None,
                                                     self.show_registrar_data),
      ('About', gtk.STOCK_ABOUT, '_About...', None, 'About Automaton',
                                                                self.on_about),
      ('Quit', None, '_Quit', None, None, self.on_quit)]
    agrp = gtk.ActionGroup('Actions')
    agrp.add_actions(actions)
    self.manager = gtk.UIManager()
    self.manager.insert_action_group(agrp, 0)
    self.manager.add_ui_from_string(menu)
    self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent

    # Dynamically build the reload menu
    if self.server is not None:
      rldmenu = gtk.Menu()
      rld = self.manager.get_widget('/Menubar/Menu/Reload')
      for plugin in sorted(self.server.loaded_plugins):
        item = gtk.MenuItem(plugin)
        item.show()
        item.connect("activate", self.on_reload)
        rldmenu.append(item)
      if len(rldmenu.get_children()) > 0:
        rld.set_submenu(rldmenu)

    self.command_log = gtk.TextBuffer()
    self.command_log_lock = threading.Lock()

    self.set_from_stock(gtk.STOCK_FIND)
    self.set_visible(True)
    self.connect('activate', self.on_command_activate)
    self.connect('popup-menu', self.on_popup_menu)

    self.build_command_window()

    self.window_active = False
    self.window_display_position = self.window.get_position()
    self.window_display_size = self.window.get_size()

  def build_command_window(self):
    """Builds the command window UI."""
    self.window_active = False
    self.window = gtk.Window()
    self.window_display_position = (300, 300)
    self.window_display_size = (300, 200)
    self.window.set_title("Automaton Command Window")
    vbox = gtk.VBox(False, 3)
    entry = gtk.Entry()
    output = gtk.TextView()
    output.set_editable(False)
    output.set_cursor_visible(False)
    output.set_buffer(self.command_log)
    output.set_wrap_mode(gtk.WRAP_WORD)
    output.set_indent(-10)
    scrollview = gtk.ScrolledWindow()
    scrollview.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
    scrollview.add(output)

    def clear_log(button):  # pylint: disable-msg=W0613
      """Clears the command history log display."""
      with locked(self.command_log_lock):
        self.command_log.delete(*self.command_log.get_bounds())
    button = gtk.Button("Clear log")
    button.connect('clicked', clear_log)

    fix = gtk.Fixed()
    fix.put(button, 0, 0)
    vbox.pack_start(entry, False, False, 0)
    vbox.pack_start(scrollview, True, True, 0)
    vbox.pack_end(fix, False, False)

    def send_command(widget, textview):
      """Interprets and executes the text entered into the text box."""
      if widget.get_text_length() > 0:
        text = widget.get_text()
        widget.set_text('')

        def cb_call(text):
          """
          Interpret the text, execute the service, and insert the 
          output into the command window.

          """
          try:
            hlp = text.split()
            if len(hlp) == 2 and hlp[0] == "help":
              output = self.server.serviceUsage(hlp[1]) or "No help available"
            else:
              registrar = self.server.registrar
              cmd, namespace, args = registrar.find_best_service(text)
              if cmd is None:
                output = "Could not parse input."
              else:
                output = registrar.request_service(cmd, namespace,
                   args) or "No output."
          except exceptions.ServiceNotProvidedError as err:
            output = str(err)
          except UnsuccessfulExecution as err:
            output = "Execution Unsuccessful: " + str(err)
          except Exception as err:
            output = "Exception encountered: " + str(err)
          output = output.strip()
          if len(output) > 0:
            with locked(self.command_log_lock):
              buf = textview.get_buffer()
              end = buf.get_end_iter()
              if buf.get_char_count() > 0:
                buf.insert(end, '\n')
              buf.insert(end, output)
              textview.scroll_mark_onscreen(buf.get_insert())
          return False

        threading.Thread(target=cb_call, args=(text,)).start()
    entry.connect('activate', send_command, output)

    self.window.connect('delete-event', self.hide_command_window)

    self.window.add(vbox)

  def on_command_activate(self, icon):  # pylint: disable-msg=W0613
    """Show the command window when the icon is clicked."""
    if self.server:
      if not self.window_active:
        self.window_active = True
        self.window.move(*self.window_display_position)
        self.window.set_size_request(*self.window_display_size)
        self.window.show_all()
        self.window.present()
      else:
        self.hide_command_window()

  def hide_command_window(self, *args):  # pylint: disable-msg=W0613
    """Hide the command window."""
    self.window.hide()
    self.window_active = False
    self.window_display_position = self.window.get_position()
    self.window_display_size = self.window.get_size()
    return True

  def show_registrar_data(self, event):  # pylint: disable-msg=W0613
    """Display information about what is stored in the registrar."""
    win = gtk.Window()
    win.set_size_request(500, 250)
    win.set_title("Registrar Data")
    vbox = gtk.VBox(False, 3)

    def get_service_data():
      """Retrieves and formats information on the registered services."""
      output = gtk.TreeStore(str)
      svc = self.server.registrar.services
      keys = svc.keys()
      for key in keys:
        parent = output.append(None, [key])
        if svc[key].usage != "":
          output.append(parent, [svc[key].usage])
      return output

    def get_object_data():
      """Retrieves and formats information on the registered objects."""
      output = gtk.TreeStore(str)
      obj = self.server.registrar.objects
      keys = obj.keys()
      for key in keys:
        parent = output.append(None, [key])
        output.append(parent, [repr(obj[key].obj)])
      return output

    data = [("Services:", get_service_data(), True),
            ("Objects:", get_object_data(), False)]

    for frame in data:
      col = gtk.TreeViewColumn(frame[0])
      view = gtk.TreeView(frame[1])
      view.append_column(col)
      render = gtk.CellRendererText()
      render.props.wrap_width = 450
      render.props.wrap_mode = gtk.WRAP_WORD
      col.pack_start(render, True)
      col.add_attribute(render, 'text', 0)
      scrollview = gtk.ScrolledWindow()
      scrollview.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
      scrollview.add(view)
      vbox.pack_start(scrollview, frame[2], frame[2], 0)

    win.add(vbox)
    win.connect('destroy', lambda x: x.destroy())
    win.show_all()
    win.present()

  def on_reload(self, item):
    """Reload the specified plugin."""
    self.server.reloadPlugin(item.get_label())

  def on_popup_menu(self, widget, button, time):
    """Display the popup menu."""
    self.menu.popup(None, None, gtk.status_icon_position_menu,
                                                          button, time, widget)

  def on_quit(self, data):  # pylint: disable-msg=W0613,R0201
    """Quit the program."""
    gtk.main_quit()

  def on_about(self, data):  # pylint: disable-msg=W0613,R0201
    """Display the About dialog."""
    dialog = gtk.AboutDialog()
    dialog.set_name('Automaton')
    dialog.set_version('0.9.0')
    dialog.set_comments('A digital life assistant.')
    dialog.set_website('http://github.com/nemec/Automaton')
    dialog.run()
    dialog.destroy()
