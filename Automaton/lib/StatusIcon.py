import os
import gtk
import threading

class StatusIcon(gtk.StatusIcon):
  def __init__(self, server):
    gtk.StatusIcon.__init__(self)
    self.server = server
    self.window_active = False
    menu = '''
      <ui>
       <menubar name="Menubar">
        <menu action="Menu">
         <menuitem action="Reload"/>
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
      for x in sorted(self.server.loadedScripts):
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

  def on_command_activate(self, icon):
    if self.server:
      if not self.window_active:
        self.window_active = True
        self.window = gtk.Window()
        self.window.set_size_request(300, 200)
        self.window.set_title("Automaton Command Window")
        vbox = gtk.VBox(False, 3)
        entry = gtk.Entry()
        output = gtk.TextView()
        output.set_editable(False)
        output.set_cursor_visible(False)
        output.set_buffer(self.command_log)
        scrollview = gtk.ScrolledWindow()
        scrollview.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
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
                  output = self.server.scriptUsage(args)
                else:
                  output = self.server.call(cmd, args)
              except self.server.Exceptions.ScriptNotLoadedException, e:
                output = e.__str__()
              except Exception, e:
                output = "Exception encountered: %s" % e
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
        
        # Prevents the window from being displayed more than once
        def window_destroy(window):
          self.window_active = False
        self.window.connect('destroy', window_destroy)

        self.window.add(vbox)
        self.window.show_all()

      # Whether it's a new window or not, present it to the user
      self.window.present()



  def on_reload(self, item):
    self.server.reloadScript(item.get_label())

  def on_popup_menu(self, widget, button, time):
    self.menu.popup(None, None, gtk.status_icon_position_menu,
                                                          button, time, widget)

  def on_quit(self, data):
    gtk.main_quit()

  def on_about(self, data):
    dialog = gtk.AboutDialog()
    dialog.set_name('Automaton')
    dialog.set_version('0.9.0')
    dialog.set_comments('A home automation application.')
    dialog.set_website('http://github.com/nemec/Automaton')
    dialog.run()
    dialog.destroy()

if __name__ == '__main__':
  StatusIcon(None)
  gtk.threads_init()
  gtk.main()

