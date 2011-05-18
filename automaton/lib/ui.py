import os
import gtk
import threading
from automaton.lib.plugin import UnsuccessfulExecution

class StatusIcon(gtk.StatusIcon):
  def __init__(self, server):
    gtk.StatusIcon.__init__(self)
    self.server = server
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
      ('Menu',  None, 'Menu'),
      ('Reload', None, 'Reload'),
      ('Registrar', None, 'Show Registrar Data', None, None,
                                                     self.show_registrar_data),
      ('About', gtk.STOCK_ABOUT, '_About...', None, 'About Automaton',
                                                                self.on_about),
      ('Quit', None, '_Quit', None, None, self.on_quit)]
    ag = gtk.ActionGroup('Actions')
    ag.add_actions(actions)
    self.manager = gtk.UIManager()
    self.manager.insert_action_group(ag, 0)
    self.manager.add_ui_from_string(menu)
    self.menu = self.manager.get_widget('/Menubar/Menu/About').props.parent

    # Dynamically build the reload menu
    if self.server is not None:
      rlmenu = gtk.Menu()
      rl = self.manager.get_widget('/Menubar/Menu/Reload')
      for x in sorted(self.server.loadedPlugins):
        item = gtk.MenuItem(x)
        item.show()
        item.connect("activate", self.on_reload)
        rlmenu.append(item)
      if len(rlmenu.get_children()) > 0:
        rl.set_submenu(rlmenu)

    self.command_log = gtk.TextBuffer()

    self.set_from_stock(gtk.STOCK_FIND)
    self.set_visible(True)
    self.connect('activate', self.on_command_activate)
    self.connect('popup-menu', self.on_popup_menu)

    self.build_command_window()


  def build_command_window(self):
    self.window_active = False
    self.window = gtk.Window()
    self.window_display_position = (300,300)
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

    def clear_log(button):
      self.command_log.delete(*self.command_log.get_bounds())
    button = gtk.Button("Clear log")
    button.connect('clicked', clear_log)

    f = gtk.Fixed()
    f.put(button,0,0)
    vbox.pack_start(entry, False, False, 0)
    vbox.pack_start(scrollview, True, True, 0)
    vbox.pack_end(f, False, False)

    def send_command(widget, textview):
      if widget.get_text_length() > 0:
        text = widget.get_text()
        widget.set_text('')
        cmd, sep, args = text.partition(' ')
        
        def cb_call(cmd, args):
          try:
            if cmd == "help":
              output = self.server.serviceUsage(args)
            else:
              output = self.server.registrar.request_service(cmd, args)
          except self.server.exceptions.ServiceNotProvidedError as e:
            output = str(e)
          except UnsuccessfulExecution as e:
            output = "Execution Unsuccessful: " + str(e)
          except Exception as e:
            output = "Exception encountered: " + str(e)
          output = output.strip()
          if len(output) > 0:
            buf = textview.get_buffer() 
            end = buf.get_end_iter()
            if buf.get_char_count() > 0:
              buf.insert(end,'\n')
            buf.insert(end, output)
            textview.scroll_mark_onscreen(buf.get_insert())
          return False

        threading.Thread(target=cb_call, args=(cmd, args)).start()      
    entry.connect('activate', send_command, output)

    self.window.connect('delete-event', self.hide_command_window)

    self.window.add(vbox)


  def on_command_activate(self, icon):
    if self.server:
      if not self.window_active:
        self.window_active = True
        self.window.move(*self.window_display_position)
        self.window.set_size_request(*self.window_display_size)
        self.window.show_all()
        self.window.present()
      else:
        self.hide_command_window()
        

  def hide_command_window(self, *args):
    self.window.hide()
    self.window_active = False
    self.window_display_position = self.window.get_position()
    self.window_display_size = self.window.get_size()
    return True


  def show_registrar_data(self, event):
    win = gtk.Window()
    win.set_size_request(500, 250)
    win.set_title("Registrar Data")
    vbox = gtk.VBox(False, 3)

    def set_buf(output, text):
      output.set_editable(False)
      output.set_cursor_visible(False)
      buf = output.get_buffer() 
      end = buf.get_end_iter()
      if buf.get_char_count() > 0:
        buf.insert(end,'\n')
      buf.insert(end, text)

    def get_service_data():
      output = gtk.TreeStore(str)
      svc = self.server.registrar.services
      keys = svc.keys()
      for key in keys:
        parent = output.append(None, [key])
        if svc[key].usage != "":
          output.append(parent, [svc[key].usage])
      return output

    def get_object_data():
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
    win.connect('destroy', lambda x :x.destroy())
    win.show_all()
    win.present()

  def on_reload(self, item):
    self.server.reloadPlugin(item.get_label())


  def on_popup_menu(self, widget, button, time):
    self.menu.popup(None, None, gtk.status_icon_position_menu,
                                                          button, time, widget)


  def on_quit(self, data):
    gtk.main_quit()


  def on_about(self, data):
    dialog = gtk.AboutDialog()
    dialog.set_name('Automaton')
    dialog.set_version('0.9.0')
    dialog.set_comments('A digital life assistant.')
    dialog.set_website('http://github.com/nemec/Automaton')
    dialog.run()
    dialog.destroy()


if __name__ == '__main__':
  StatusIcon(None)
  gtk.threads_init()
  gtk.main()

