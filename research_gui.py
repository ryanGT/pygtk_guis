#!/usr/bin/env python
"""This module will provide the base class for my research pygtk guis
for use with Real_Time_Python or the SFLR."""
import pygtk
pygtk.require('2.0')
import gtk

import input_generation

from matplotlib.figure import Figure
#from numpy import arange, sin, pi, cos, array, zeros, int64
from numpy import *

# uncomment to select /GTK/GTKAgg/GTKCairo
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas


class base_class(object):
    """This is the base class for all research guis that use pygtk to
    run tests using Real_Time_Python.  All guis have a
    self.control_vbox on the left and a self.main_hbox that contains
    the control_vbox and the figure canvas.  self.control_vbox is
    required to have an input generation notebook in the middle of it
    with controls above or below it added in the methods
    add_controls_above_notebook and add_controls_below_notebook.  If
    these methods simply pass, there will not be any controls above or
    below the notebook."""
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
        self.test.Close_Serial()
        gtk.main_quit()


    def add_controls_above_notebook(self):
        pass


    def add_controls_below_notebook(self):
        pass


    def __init__(self, debug=0):
        self.debug = debug
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

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
        self.window.set_border_width(10)

        
        main_hbox = gtk.HBox(homogeneous=False, spacing=5)
        control_vbox = gtk.VBox(homogeneous=False, spacing=5)
        self.control_vbox = control_vbox#control_vbox is assumed to be
                                        #the name of the vbox on the
                                        #left of the gui

        self.add_controls_above_notebook()
        self.add_notebook()
        self.add_run_test_button()
        self.add_save_data_button()
        main_hbox.pack_start(self.control_vbox, False, False, 0)
        self.main_hbox = main_hbox
        self.window.add(self.main_hbox)
