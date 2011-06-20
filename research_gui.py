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
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas

import time, copy, os

pack_args_w_pad = (False, False, 5)

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
        if hasattr(self, 'test'):
            self.test.Close_Serial()
        gtk.main_quit()


    def save_data(self, widget, data=None):
        """This method saves the data on the figure canvas to a text
        file.  It assumes that the plot method set the parameter
        self.save_test.  It is the data from this test that gets
        saved."""
        dialog = gtk.FileChooserDialog("Save As..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       #gtk.FILE_CHOOSER_ACTION_OPEN,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE, gtk.RESPONSE_OK))
            #gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filter = gtk.FileFilter()
        filter.set_name("txt files")
        filter.add_pattern("*.txt")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)


        response = dialog.run()
        out = None
        if response == gtk.RESPONSE_OK:
            print dialog.get_filename(), 'selected'
            out = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            print 'Closed, no files selected'
        dialog.destroy()

        if out is not None:
            fno, ext = os.path.splitext(out)
            self.save_test.Save(fno)


    def plot_results(self, legloc=4, test=None):
        if test is None:
            test = self.test

        self.save_test = test
        
        self.ax.cla()
        self.t = test.nvect*self.test.dt
        for attr, label in zip(self.plot_attrs, self.plot_labels):
            if hasattr(test, attr):
                data = getattr(test, attr)
                self.ax.plot(self.t, data, label=label)
        self.ax.legend(loc=legloc)
        self.ax.set_xlabel('Time (sec.)')
        self.ax.set_ylabel('Signal Amplitude (counts)')
        self.fig.canvas.draw()


    def add_controls_above_notebook(self):
        pass


    def add_controls_below_notebook(self):
        pass


    def add_notebook(self):
        self.input_notebook = input_generation.input_gen_notebook()
        self.input_notebook.show()
        self.control_vbox.pack_start(self.input_notebook, *pack_args_w_pad)# True, True, 5)


    def run_test(self, widget, data=None):
        pass

    
    def add_run_test_button(self):
        self.run_test_button = gtk.Button("Run Test")
        # Add the run_test button to the gui
        self.control_vbox.pack_start(self.run_test_button, *pack_args_w_pad)
        self.run_test_button.connect("clicked", self.run_test, None)


    def add_save_data_button(self):
        self.save_data_button = gtk.Button("Save Data")
        # Add the run_test button to the gui
        self.control_vbox.pack_start(self.save_data_button, *pack_args_w_pad)
        self.save_data_button.connect("clicked", self.save_data, None)


    def add_figure_canvas(self):
        """Note: this method assumed self.main_hbox is already
        defined.  A figure canvas with a toolbar at the bottom is
        added to self.main_hbox."""
        self.fig = Figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        t = arange(0.0,3.0,0.01)
        s = sin(2*pi*t)
        self.ax.plot(t,s)

        self.figcanvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
        self.figcanvas.show()
        self.canvas_vbox = gtk.VBox()
        toolbar = NavigationToolbar(self.figcanvas, self.window)
        #toolbar.set_size_request(-1,50)
        self.figcanvas.set_size_request(600,300)
        toolbar.set_size_request(600,50)
        toolbar.show()
        self.canvas_vbox.pack_start(self.figcanvas)#, expand=True, \
            #fill=True, padding=5)
        self.canvas_vbox.pack_start(toolbar, False)#, False)#, padding=5)
        self.main_hbox.pack_start(self.canvas_vbox)#, expand=True, \
            #fill=True, padding=5)

        
    def __init__(self, title='Research GUI', \
                 plot_attrs=['uvect','yvect'], \
                 plot_labels=['u','$\\theta$'], \
                 width=1000, height=700, debug=0):
        self.debug = debug
        self.plot_attrs = plot_attrs
        self.plot_labels = plot_labels
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
        self.main_hbox = main_hbox
        control_vbox = gtk.VBox(homogeneous=False, spacing=5)
        self.control_vbox = control_vbox#control_vbox is assumed to be
                                        #the name of the vbox on the
                                        #left of the gui

        self.add_controls_above_notebook()
        self.add_notebook()
        self.add_run_test_button()
        self.add_save_data_button()
        self.add_controls_below_notebook()

        #add the two main vboxes (control_vbox and canvas_vbox) to the hbox:
        main_hbox.pack_start(self.control_vbox, False, False, 0)
        self.add_figure_canvas()

        self.window.add(self.main_hbox)

        self.window.set_size_request(width, height)

        self.window.set_title(title)
        # and the window
        #self.window.show()
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.show_all()


    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()


if __name__ == "__main__":
    myapp = base_class()
    #myapp.window.resize(400,300)
    myapp.main()
