#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import glob, os, pdb, socket, shutil, datetime, time, numpy

import rwkmisc, listbox, image_on_scrolled_window

pack_args_w_pad = (False, False, 5)

class BD_MIL_app(rwkmisc.object_that_saves):
    def save(self, widget=None, data=None):
        raise NotImplementedError


    def refresh_bd(self, widget=None, data=None):
        raise NotImplementedError
    

    def edit_preferences(self, widget=None, data=None):
        raise NotImplementedError


    def changed_cb(self, combobox):
        # see example in /home/ryan/python_stuff/pygtk_learn/comboboxbasic.py:
        model = combobox.get_model()
        index = combobox.get_active()
        if index:
            print 'You chose ', model[index][0]
        return
    
    
    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False


    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        #self.save(settings_path)
        gtk.main_quit()


    def __init__(self):
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)


        self.ui = """<ui>
        <menubar name="MenuBar">
            <menu action="File">
                <menuitem action="Save"/>
                <menuitem action="Quit"/>
            </menu>
            <menu action="Preferences">
                <menuitem action="Edit Preferences"/>
            </menu>
        </menubar>
        </ui>"""


        uimanager = gtk.UIManager()

        # Add the accelerator group to the toplevel window
        self.accelg = uimanager.get_accel_group()
        self.window.add_accel_group(self.accelg)

        actiongroup = gtk.ActionGroup('UIManagerExample')
        self.actiongroup = actiongroup

        # Create a ToggleAction, etc.
        actiongroup.add_actions([('Save', None, '_Save',
                                 '<control>s', 'Save', self.save),
                                 ('Quit', gtk.STOCK_QUIT, '_Quit', None,
                                  'Quit the Program', self.destroy),
                                 ('File', None, '_File'),
                                 ('Edit Preferences', None, 'Edit Preferences',
                                  '<alt>e', 'Edit Preferences', self.edit_preferences),
                                 ('Preferences', None, '_Preferences'),
                                 ])
        actiongroup.get_action('Quit').set_property('short-label', '_Quit')
        #actiongroup.get_action('Quit').set_property('short-label', '_Quit')

        uimanager.insert_action_group(actiongroup, 0)
        # Add a UI description
        uimanager.add_ui_from_string(self.ui)

        # Create a MenuBar

        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)

        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)

        # Sets the border width of the window.
        self.window.set_border_width(2)

        ## self.store = gtk.ListStore(gtk.gdk.Pixbuf)
        ## self.icon_view = gtk.IconView(self.store)
        ## self.icon_view.set_pixbuf_column(0)
        ## self.icon_view.set_selection_mode(gtk.SELECTION_MULTIPLE)

        ## self.folder = '/mnt/personal/pictures/Joshua_Ryan/2011/Mar_2011/Eli/thumbnails/'
        ## self.pat = os.path.join(self.folder, '*.jpg')
        ## self.thumbnail_paths = glob.glob(self.pat)
        ## self.thumbnail_paths.sort()

        ## for arg in self.thumbnail_paths:
        ##     pixbuf = gtk.gdk.pixbuf_new_from_file(arg)
        ##     self.store.append((pixbuf, ))

        ## self.sw = gtk.ScrolledWindow()

        ## self.icon_view.connect("selection-changed", self.on_item_activated)

        ## self.sw.add(self.icon_view)

        self.DEF_PAD = 5
        self.DEF_PAD_SMALL = 3
        
        self.main_vbox = gtk.VBox(homogeneous=False, spacing=0)

        self.menubar = uimanager.get_widget('/MenuBar')
        self.main_vbox.pack_start(self.menubar, False)

        #self.hpaned = gtk.HPaned()
        self.h1 = gtk.HBox(homogeneous=False, spacing=0)
        #self.main_vbox.pack_start(self.hpaned, True)
        self.main_vbox.pack_start(self.h1, True)
        #self.hpaned.show()
        self.h1.show()

        # Now create the contents of the two halves of the window
        self.image_on_sw = image_on_scrolled_window.image_on_scrolled_window()
        self.image_on_sw.set_size_request(750,200)
        #self.hpaned.add1(self.image_on_sw)
        self.h1.pack_start(self.image_on_sw, *pack_args_w_pad)
        hard_coded_path = '/home/ryan/siue/Research/papers/ASEE_IL_IN_BD_MIL/tikz_sys_test.jpg'
        self.image_on_sw.set_from_path(hard_coded_path)
        self.image_on_sw.show()

        self.refresh_button = gtk.Button("Refresh")
        # Add the run_test button to the gui
        self.v1_h1 = gtk.VBox()
        self.v1_h1.pack_start(self.refresh_button, True, False)
        self.h1.pack_start(self.v1_h1, *pack_args_w_pad)
        self.refresh_button.connect("clicked", self.refresh_bd, None)


        #self.hpaned.add2(self.notebook)
        #self.notebook.show()

        ##############################################################
        #
        # This is the section that adds, edits, and deletes blocks
        #
        ##############################################################
        big_frame_hbox = gtk.HBox()
        block_frame = gtk.Frame("Blocks")
        big_frame_hbox.pack_start(block_frame)
        self.main_vbox.pack_start(big_frame_hbox, True)
        ## vbox2.pack_start(frame, True, True, self.DEF_PAD)
        vbox_block_frame = gtk.VBox(False, self.DEF_PAD_SMALL)
        block_frame.add(vbox_block_frame)

        block_frame_h1 = gtk.HBox()

        self.block_combobox = gtk.combo_box_new_text()
        block_frame_h1.pack_start(self.block_combobox, False, False, 0)
        vbox_block_frame.pack_start(block_frame_h1)
        self.block_combobox.append_text('block type:')
        self.block_combobox.append_text('source')
        self.block_combobox.append_text('TF')
        self.block_combobox.append_text('output')
        self.block_combobox.connect('changed', self.changed_cb)
        self.block_combobox.show()
        self.block_combobox.set_active(0)


        self.block_placement_cb = gtk.combo_box_new_text()
        block_frame_h1.pack_start(self.block_placement_cb, False, False, 0)
        self.block_placement_cb.append_text('placement:')
        self.block_placement_cb.append_text('absolute')
        self.block_placement_cb.append_text('right of')
        self.block_placement_cb.append_text('left of')
        self.block_placement_cb.append_text('above of')
        self.block_placement_cb.append_text('below of')        
        self.block_placement_cb.connect('changed', self.changed_cb)
        self.block_placement_cb.show()
        self.block_placement_cb.set_active(0)

        


        self.block_listbox = listbox.listbox('Block List', initial_data=['input - u', \
                                                                         'sum1', \
                                                                         'controller - G_c', \
                                                                         'plant - G', \
                                                                         'output - y'])
        block_frame_h2 = gtk.HBox()
        block_frame_h2.pack_start(self.block_listbox, False, False, 0)
        self.block_listbox.show()
        vbox_block_frame.pack_start(block_frame_h2, False)

        temp_hbox = gtk.HBox()
        self.add_block_button = gtk.Button("Add")
        temp_hbox.pack_start(self.add_block_button, True, False)
        self.update_block_button = gtk.Button("Edit Parameters")
        temp_hbox.pack_start(self.update_block_button, True, False)
        self.remove_block_button = gtk.Button("Remove")
        temp_hbox.pack_start(self.remove_block_button, True, False)
        temp_vbox = gtk.VBox()
        temp_vbox.pack_start(temp_hbox, True, False, self.DEF_PAD)
        block_frame_h2.pack_start(temp_vbox, False, False, self.DEF_PAD)
        #self.refresh_button.connect("clicked", self.refresh_bd, None)
        


        ##############################################################
        #
        # End block editting section
        #
        ##############################################################


        ##############################################################
        #
        # This is the section that adds, edits, and deletes wires
        #
        ##############################################################
        wire_frame = gtk.Frame("wires")
        #self.main_vbox.pack_start(wire_frame, True)
        big_frame_hbox.pack_start(wire_frame, True)
        ## vbox2.pack_start(frame, True, True, self.DEF_PAD)
        vbox_wire_frame = gtk.VBox(False, self.DEF_PAD_SMALL)
        wire_frame.add(vbox_wire_frame)

        wire_frame_h1 = gtk.HBox()

        self.wire_combobox = gtk.combo_box_new_text()
        wire_frame_h1.pack_start(self.wire_combobox, False, False, 0)
        vbox_wire_frame.pack_start(wire_frame_h1)
        self.wire_combobox.append_text('wire type:')
        self.wire_combobox.append_text('source')
        self.wire_combobox.append_text('TF')
        self.wire_combobox.append_text('output')
        self.wire_combobox.connect('changed', self.changed_cb)
        self.wire_combobox.show()
        self.wire_combobox.set_active(0)


        self.wire_listbox = listbox.listbox('Wire List', initial_data=['wire1', \
                                                                       'wire2', \
                                                                       'wire3', \
                                                                       'wire4', \
                                                                       'feedback wire'])
        wire_frame_h2 = gtk.HBox()
        wire_frame_h2.pack_start(self.wire_listbox, False, False, 0)
        self.wire_listbox.show()
        vbox_wire_frame.pack_start(wire_frame_h2, False)

        temp_hbox = gtk.HBox()
        self.add_wire_button = gtk.Button("Add")
        temp_hbox.pack_start(self.add_wire_button, True, False)
        self.update_wire_button = gtk.Button("Edit Parameters")
        temp_hbox.pack_start(self.update_wire_button, True, False)
        self.remove_wire_button = gtk.Button("Remove")
        temp_hbox.pack_start(self.remove_wire_button, True, False)
        temp_vbox = gtk.VBox()
        temp_vbox.pack_start(temp_hbox, True, False, self.DEF_PAD)
        wire_frame_h2.pack_start(temp_vbox, False, False, self.DEF_PAD)
        #self.refresh_button.connect("clicked", self.refresh_bd, None)



        ##############################################################
        #
        # End wire editting section
        #
        ##############################################################
        
        ## for i in range(len(flags)):
        ##     toggle = gtk.CheckButton(flags[i])
        ##     toggle.connect("toggled", self.calendar_toggle_flag)
        ##     vbox3.pack_start(toggle, True, True, 0)
        ##     self.flag_checkboxes[i] = toggle

        self.window.add(self.main_vbox)

        ## self.saveattrs = ['database_path']
        ## if os.path.exists(settings_path):
        ##     self.load(settings_path)
        #print('self.database_path = %s' % self.database_path)

        #pn1 = self.notebook.get_current_page()
        #self.notebook.show()
        #????#self.window.set_size_request(1200,700)
        #self.notebook.set_current_page(1)
        #pn2 = self.notebook.get_current_page()
        #print('pn1 = %s' % pn1)
        #print('pn2 = %s' % pn2)
        self.window.show_all()
        #self.notebook.next_page()
        #print('pn3 = %s' % pn2)


    
    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()


# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    myapp = BD_MIL_app()
    myapp.main()
