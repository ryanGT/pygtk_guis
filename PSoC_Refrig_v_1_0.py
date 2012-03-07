#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import research_gui
import input_generation

from matplotlib.figure import Figure
#from numpy import arange, sin, pi, cos, array, zeros, int64
import numpy
from numpy import *

# uncomment to select /GTK/GTKAgg/GTKCairo
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar

#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas

#import Real_Time_Python as RTP
import controls
import time, copy, os


import serial_utils as SU
reload(SU)


log_file = 'Python_PSoC_Refrig_data.txt'


def _list_to_row_str(listin):
    string_out = '\t'.join(listin) + '\n'
    return string_out



def run_OL_test(cmd_resistance=255, run_time=7.0, freq=1.0/7):
    """cmd_resistance is a command signal sent to the PSoC.  1 corresponds to maximum RPM.  255 is minimum."""
    ser = Open_Serial()
    Start_Test(ser)
    N = int(run_time*60*60*freq)
    print(N)
    #N = 10

    fmt = '%0.2f'

    if not os.path.exists(log_file):
        f = open(log_file, 'w')
        #write the column labels
        label_row = ['Time Stamp','Python count i','PSoC Count n','Command Resistance','RPM','Temp 1 (C)','Temp 2 (C)']
        label_str = _list_to_row_str(label_row)
        f.write(label_str)
    else:
        f = open(log_file, 'a')

    #Send the Open Loop command
    Send_One_Voltage(ser,cmd_resistance)
    switched = 0

    for i in range(N):
        if (i > 1800) and (not switched):
            cmd_resistance = 1
            Send_One_Voltage(ser,cmd_resistance)
            switched = 1

        n, t1, t2 = Poll_Temps(ser)

        t1_str = fmt % t1
        t2_str = fmt % t2

        RPM_str = Poll_RPM(ser)

        time_stamp = time.strftime('%m/%d/%Y %H:%M:%S')
        i_str = '%i' % i
        n_str = '%i' % n
        cmd_str = '%i' % cmd_resistance
        row_list = [time_stamp, i_str, n_str, cmd_str, RPM_str, t1_str, t2_str]
        row_str = _list_to_row_str(row_list)
        print(row_str[0:-1])
        f.write(row_str)

        time.sleep(7.0)

    Send_One_Voltage(ser,0)
    f.close()
    Close_Serial(ser)


Entry_width = 50
max_len = 10
myspace = 5
pack_args_pad = (False, False, 5)
args_no_pad = (False, False, 0)
pack_args_w_pad = (False, False, 5)


import threading

class test_thread(threading.Thread):
    def __init__(self, GUI, des_temp, N, \
                 fake_serial=False):
        threading.Thread.__init__(self)
        self.GUI = GUI
        self.des_temp = des_temp
        self.N = N
        self.fake_serial = fake_serial
        self.t0 = None


    def Open_Serial(self):
        self.ser = SU.Open_Serial()
        return self.ser


    def Close_Serial(self):
        SU.Close_Serial(self.ser)


    def Send_One_Voltage(self, v=0):
        SU.WriteByte(self.ser, 47)
        SU.WriteInt(self.ser, v)


    def Poll_Temps(self, out_case=1):
        """out_case = 0 means just output the raw integers.
        out_case = 1 means output degrees Celcius.
        out_case = 2 means convert to Farnheit."""
        SU.WriteByte(self.ser,2)
        n = SU.Read_Two_Bytes_Twos_Comp(self.ser)
        t1 = SU.Read_Two_Bytes_Twos_Comp(self.ser)
        t2 = SU.Read_Two_Bytes_Twos_Comp(self.ser)

        if out_case > 0:
            t1 = t1/4.0
            t2 = t2/4.0
        if out_case == 2:
            t1 = t1*9.0/5.0+32
            t2 = t2*9.0/5.0+32


        return n, t1, t2
        

    def Read_Message(self, sendbyte=1):
        SU.WriteByte(self.ser, sendbyte)
        Null = '\x00'
        msg = ''
        N = 100
        i = 0
        while i < N:#not quite a while 1
            cur_byte = self.ser.read(1)
            if cur_byte in ['',Null]:
                break
            else:
                cur_ord = ord(cur_byte)
                msg += cur_byte
                i += 1

        return msg


    def Poll_RPM(self):
        #msg = Read_Message(ser, sendbyte=3)
        SU.WriteByte(self.ser, 3)
        Null = '\x00'
        msg = ''
        N = 10
        i = 0
        while i < N:#not quite a while 1
            cur_byte = self.ser.read(1)
            if cur_byte in ['',Null]:
                break
            else:
                #print('cur_byte = %s' % cur_byte)
                cur_ord = ord(cur_byte)
                msg += cur_byte
                i += 1
        return msg


    def Start_Test(self):
        self.ser.flushOutput()
        self.ser.flushInput()
        self.ser.timeout = 15
        SU.WriteByte(self.ser, 113)



    def read_data(self, i=-1):
        if self.fake_serial:
            n = i
            t1 = 23 - 0.5*i
            t2 = 25 - 0.75*i
            RPM = 4500.25
        else:
            n, t1, t2 = self.Poll_Temps()
            RPM_str = self.Poll_RPM()
            RPM = float(RPM_str)

        return n, t1, t2, RPM


    def set_GUI_data(self, i, n, t1, t2, RPM, cur_minutes):
        t_a = (t1+t2)*0.5
        self.GUI.e[i] =  self.des_temp - t_a
        self.GUI.t_d[i] = self.des_temp
        self.GUI.t1[i] = t1
        self.GUI.t2[i] = t2
        self.GUI.ta[i] = t_a
        self.GUI.i_vect[i] = i
        self.GUI.n_vect[i] = n
        self.GUI.RPM[i] = RPM
        self.GUI.time[i] = cur_minutes


    def run(self):
        for i in range(self.N):
            if self.t0 is None:
                self.t0 = time.time()
                cur_minutes = 0.0
            else:
                cur_time = time.time()
                cur_minutes = (cur_time-self.t0)/60.0

            n, t1, t2, RPM = self.read_data(i)
            self.set_GUI_data(i, n, t1, t2, RPM, cur_minutes)
            cmd = self.GUI.calc_cmd(i)


            if not self.fake_serial:
                self.Send_One_Voltage(cmd)


            log_str = self.GUI.build_log_str(i)
            gobject.idle_add(self.GUI.append_to_log, log_str)
            self.GUI.save_to_log_file(log_str)

            gobject.idle_add(self.GUI.update_plot, i)
            
            #time.sleep(7.0)
            if self.GUI.break_test:
                gobject.idle_add(self.GUI.append_to_log, "break acknowledged")
                break
            else:
                if self.fake_serial:
                    time.sleep(1.0)
                else:
                    time.sleep(7.0)


        if not self.fake_serial:
            self.Send_One_Voltage(0)
            self.Close_Serial()
            gobject.idle_add(self.GUI.append_to_log, "Stop signal sent to PSoC.")

        gobject.idle_add(self.GUI.append_to_log, "Test Ended.")





class input_page(gtk.VBox):
    def __init__(self, title, labels, attrs, defaults):
        gtk.VBox.__init__(self, homogeneous=False, spacing=myspace)
        self.title = title
        for label, attr, default in zip(labels, attrs, defaults):
            entry = gtk.Entry()
            mylabel = gtk.Label(label)
            mylabel.show()
            entry.set_size_request(Entry_width, -1)
            entry.set_max_length(max_len)
            entry.set_text(default)
            entry.show()
            setattr(self, attr, entry)
            hbox = gtk.HBox(homogeneous=False)
            hbox.pack_end(entry, *pack_args_pad)
            hbox.pack_end(mylabel, *pack_args_pad)
            self.pack_start(hbox, *args_no_pad)



    def _create_u_zeros(self, dtype=numpy.float64):
        dur_text = self.dur.get_text()
        duration = int(dur_text)
        u = numpy.zeros(duration, dtype=dtype)
        return u


    def create_u_vect(self):
        raise NotImplementedError


    def _get_text(self, entry_attr):
        entry = getattr(self, entry_attr)
        text = entry.get_text()
        return text


    def _get_int(self, entry_attr):
        text = self._get_text(entry_attr)
        out = int(text)
        return out


    def _get_float(self, entry_attr):
        text = self._get_text(entry_attr)
        out = float(text)
        return out



class CL_page(input_page):
    def __init__(self, title='Closed-Loop', \
                 labels=['desired temp (C)', 'test duration (hours)', 'Kp'], \
                 attrs=['des_temp', 'duration', 'Kp',], \
                 defaults=['-10.0', '4.0', '50']):
        input_page.__init__(self, title=title, \
                            labels=labels, \
                            attrs=attrs, \
                            defaults=defaults)


class my_notebook(gtk.Notebook):
    def _create_pages(self):
        class_list = [CL_page]
        attr_list = ['CL_page']
        self.pages = []
        for cur_class, attr in zip(class_list, attr_list):
            page = cur_class()
            setattr(self, attr, page)
            tab_label = gtk.Label(page.title)
            self.append_page(page, tab_label)
            self.pages.append(page)


    def __init__(self, *args, **kwargs):
        gtk.Notebook.__init__(self, *args, **kwargs)
        self.set_tab_pos(gtk.POS_TOP)
        self.show()
        self._create_pages()


class PSoC_Refrig_gui(research_gui.base_class):
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



    def add_notebook(self):
        self.input_notebook = my_notebook()
        self.input_notebook.show()
        self.control_vbox.pack_start(self.input_notebook, *pack_args_w_pad)# True, True, 5)


    def calc_cmd(self, i):
        self.cmd_raw[i] = 50.0*self.e[i]+125#offset of 125 to linearize about
            #the middle of the operating range
        cmd_out = self.cmd_raw[i]

        #handle saturation
        if cmd_out > 255:
            cmd_out = 255
        elif cmd_out < 1:
            cmd_out = 1
        self.cmd[i] = int(cmd_out)
        return self.cmd[i]


    def build_log_str(self, i):
        fmt = '%0.4g'
        t1_str = fmt % self.t1[i]
        t2_str = fmt % self.t2[i]

        time_stamp = time.strftime('%m/%d/%Y %H:%M:%S')
        i_str = '%i' % self.i_vect[i]
        n_str = '%i' % self.n_vect[i]
        cmd_str = '%i' % self.cmd[i]
        t_des_str = fmt % self.t_d[i]
        e_str = fmt % self.e[i]
        RPM_str = '%0.6g' % self.RPM[i]
        row_list = [time_stamp, i_str, n_str, t_des_str, e_str, cmd_str, RPM_str, t1_str, t2_str]
        row_str = _list_to_row_str(row_list)
        return row_str


    def save_to_log_file(self, msg):
        f = open(self.log_file, 'a')
        f.write(msg)
        f.close()
        
        

    def stop_test(self, widget, data=None):
        self.append_to_log("Stopping test (it may take several seconds for this to take effect).")
        self.break_test = True


    def run_test(self, widget, data=None, fake_data=True):
        self.clear_log()
        self.append_to_log("Starting new test.")
        self.des_temp = self.input_notebook.CL_page._get_float('des_temp')#, 'duration', 'Kp',], \)
        self.duration = self.input_notebook.CL_page._get_float('duration')#, 'duration', 'Kp',], \)
        self.Kp = self.input_notebook.CL_page._get_float('Kp')

        des_temp_msg = 'Desired Temp. (C) = %0.4g' % self.des_temp
        self.append_to_log(des_temp_msg)

        dur_msg = 'test duration (hours) = %0.4g' % self.duration
        self.append_to_log(dur_msg)

        Kp_msg = 'Kp = %0.4g' % self.Kp
        self.append_to_log(Kp_msg)

        if not fake_data:
            self.Open_Serial()
            self.Start_Test()
            
        N = int(self.duration*60.0*60.0/self.dt)
        #N = 10
        self.N = N
        N_msg = 'N = %i' % N
        self.append_to_log(N_msg)
        #N = 10

        self.e = zeros(N)
        self.cmd_raw = zeros(N)
        self.cmd = zeros(N)
        self.n_vect = zeros(N)
        self.i_vect = zeros(N)
        self.t1 = zeros(N)
        self.t2 = zeros(N)
        self.ta = zeros(N)
        self.t_d = zeros(N)
        self.RPM = zeros(N)
        self.time = zeros(N)

        fmt = '%0.2f'

        label_row = ['Time Stamp','Python count i','PSoC Count n','Desired Temp.','Error Signal','Command Resistance','RPM','Temp 1 (C)','Temp 2 (C)']
        self.labels = label_row
        label_str = _list_to_row_str(label_row)

        self.append_to_log('')
        self.append_to_log(label_str)
        
        if not os.path.exists(self.log_file):
            f = open(self.log_file, 'w')
            #write the column labels
            f.write(label_str)
            f.close()

        self.break_test = False
        self.t0 = None
        self.t0_stamp = time.strftime('%m/%d/%Y %H:%M:%S')
        self.test_thread = test_thread(self, \
                                       des_temp=self.des_temp, \
                                       N=self.N, \
                                       fake_serial=False)
        self.test_thread.start()
        

    def append_to_log(self, msg, scroll=True):
        if msg == '':
            msg = '\n'
        elif msg[-1] != '\n':
            msg += '\n'
        end_iter = self.textbuffer.get_end_iter()
        self.textbuffer.insert(end_iter, msg)

        if scroll:
            #mark = self.textbuffer.get_insert()
            #self.textview.scroll_to_mark(mark, 0.01)
            #end_iter = self.textbuffer.get_end_iter()
            #mymark = self.textbuffer.create_mark("mymark", end_iter, False)
            #self.textview.scroll_to_mark(mymark, 0.45)
            #self.textview.scroll_to_iter(end_iter, 0.01)
            #self.textview.scroll_mark_onscreen(self.textbuffer.get_insert())
            #self.textview.scroll_to_mark(self.textbuffer.get_insert(), 0)
            adj = self.text_scrollw.get_vadjustment()
            adj.set_value( adj.upper )# - adj.pagesize )
            

    def clear_log(self):
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        self.textbuffer.delete(start_iter, end_iter)


    def add_run_test_button(self):
        self.run_test_button = gtk.Button("Start Test")
        # Add the run_test button to the gui
        self.control_vbox.pack_start(self.run_test_button, *pack_args_w_pad)
        self.run_test_button.connect("clicked", self.run_test, None)


    def add_stop_test_button(self):
        self.run_test_button = gtk.Button("Stop Test")
        # Add the run_test button to the gui
        self.control_vbox.pack_start(self.run_test_button, *pack_args_w_pad)
        self.run_test_button.connect("clicked", self.stop_test, None)


    def add_save_data_button(self):
        self.save_data_button = gtk.Button("Save Data")
        # Add the run_test button to the gui
        self.control_vbox.pack_start(self.save_data_button, *pack_args_w_pad)
        self.save_data_button.connect("clicked", self.save_data, None)



## lns1 = ax.plot(time, Swdown, '-', label = 'Swdown')
## lns2 = ax.plot(time, Rn, '-', label = 'Rn')
## ax2 = ax.twinx()
## lns3 = ax2.plot(time, temp, '-r', label = 'temp')

## # added these three lines
## lns = lns1+lns2+lns3
## labs = [l.get_label() for l in lns]
## ax.legend(lns, labs, loc=0)

    def _label_axes(self):
        self.ax1.set_ylabel('Temp. (C)')
        self.ax1.set_xlabel('Time (minutes)')
        self.ax2.set_ylabel('RPM')
        self.ax3.set_ylabel('Command')

        
    def add_figure_canvas(self, w=700, h=500):
        """Note: this method assumed self.main_hbox is already
        defined.  A figure canvas with a toolbar at the bottom is
        added to self.main_hbox."""
        self.fig = Figure(figsize=(8,6), dpi=100)
        fig_W = 0.725
        fig_L = 0.125
        fig_1_B = 0.1
        fig_1_H = 0.5
        self.ax1 = self.fig.add_axes([fig_L,fig_1_B,fig_W,fig_1_H])#self.fig.add_subplot(111)
        fig_2_B = 0.7
        fig_2_H = 0.25
        self.ax2 = self.fig.add_axes([fig_L,fig_2_B,fig_W,fig_2_H])
        self.ax3 = self.ax2.twinx()
        t = arange(0.0,3.0,0.01)
        s = sin(2*pi*t)
        s2 = cos(2*pi*t)
        s3 = 10*sin(5*pi*t)
        self.ax1.plot(t,s)
        self.ax2.plot(t,s2,'r-')
        self.ax3.plot(t,s3,'g-')

        self._label_axes()
        
        self.figcanvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
        self.figcanvas.show()
        self.canvas_vbox = gtk.VBox()
        toolbar = NavigationToolbar(self.figcanvas, self.window)
        #toolbar.set_size_request(-1,50)
        self.figcanvas.set_size_request(w,h)
        toolbar.set_size_request(w,50)
        toolbar.show()
        self.canvas_vbox.pack_start(self.figcanvas)#, expand=True, \
            #fill=True, padding=5)
        self.canvas_vbox.pack_start(toolbar, False)#, False)#, padding=5)
        self.main_hbox.pack_start(self.canvas_vbox)#, expand=True, \
            #fill=True, padding=5)



    def update_plot(self, i):
        ## self.e = zeros(N)
        ## self.cmd_raw = zeros(N)
        ## self.cmd = zeros(N)
        ## self.n_vect = zeros(N)
        ## self.i_vect = zeros(N)
        ## self.t1 = zeros(N)
        ## self.t2 = zeros(N)
        ## self.ta = zeros(N)
        ## self.t_d = zeros(N)
        ## self.RPM = zeros(N)
        ## self.time = zeros(N)
        
        if i < 2:
            #do nothing
            return
        x = self.time[0:i+1]

        #plot on main axis
        ax1_list = ['t_d','t1','t2','ta']
        ax1_labels = ['$t_{desired}$','$t_1$','$t_2$','$t_{ave}$']
        self.ax1.cla()
        for attr, label in zip(ax1_list, ax1_labels):
            vect = getattr(self, attr)
            self.ax1.plot(x, vect[0:i+1])
        self.ax1.legend(ax1_labels, loc=4)

        #plot RPM on ax2
        self.ax2.cla()
        self.ax2.plot(x, self.RPM[0:i+1])

        self.ax3.cla()
        self.ax3.plot(x, self.cmd[0:i+1])

        self._label_axes()

        self.fig.canvas.draw()


    def save_data_dialog(self):
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
            msg = dialog.get_filename() +  ' selected'
            out = dialog.get_filename()
        elif response == gtk.RESPONSE_CANCEL:
            msg = 'Closed, no files selected'
        dialog.destroy()
        self.append_to_log(msg)

        return out


    def save_data_to_txt(self, filepath, delim='\t'):
        fno, ext = os.path.splitext(filepath)
        if not ext:
            filepath += '.txt'
            
        f = open(filepath, 'w')
        
        def out(msg):
            f.write(msg + '\n')

        def cout(msg):
            out('#' + msg)
            
        cout('Closed-Loop PSoC Refrig test')
        cout('Started at ' + self.t0_stamp)
        cout('Kp = %0.5g' % self.Kp)
        cout('Desired Temp. = %0.5g' % self.des_temp)
        ## self.e = zeros(N)
        ## self.cmd_raw = zeros(N)
        ## self.cmd = zeros(N)
        ## self.n_vect = zeros(N)
        ## self.i_vect = zeros(N)
        ## self.t1 = zeros(N)
        ## self.t2 = zeros(N)
        ## self.ta = zeros(N)
        ## self.t_d = zeros(N)
        ## self.RPM = zeros(N)
        ## self.time = zeros(N)
        labels = ['Time (minutes)','t_desired (C)','i Python index','n PSoC index', \
                  't1 (C)','t2 (C)','t_ave (C)','Error (C)', 'Command Signal (counts)', \
                  'RPM']
        cout(delim.join(labels))
        vectorlist = [self.time, self.t_d, self.i_vect, self.n_vect, \
                      self.t1, self.t2, self.ta, self.e, self.cmd, self.RPM]
        fmt = '%0.10g'
        mymatrix = column_stack(vectorlist)#create a matrix with each vector as a column
        savetxt(f, mymatrix, fmt=fmt, delimiter=delim)
        f.close()


    def save_data(self, widget, data=None):
        """This method saves the data on the figure canvas to a text
        file.  It assumes that the plot method set the parameter
        self.save_test.  It is the data from this test that gets
        saved."""
        out = self.save_data_dialog()
        if out is not None:
            self.save_data_to_txt(out)
            

    def __init__(self, debug=0):
        ## attrs = ['uvect','vvect','yvect','avect','thd_hatvect']
        ## labels = ['u','v','$\\theta$','a','$\\hat{\\theta}_d$']
        self.dt = 7.0
        self.log_file = 'Python_PSoC_Refrig_data_CL.txt'
        self.break_test = False
        
        title = 'PSoC Refrigeration v. 1.0.0'
        width=1000
        height=700
        
        self.debug = debug
        self.plot_attrs = ['t1','t2','ta']
        self.plot_labels = ['$t_1$','$t_2$','$t_a$']
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


        main_vbox = gtk.VBox(homogeneous=False, spacing=5)
        main_hbox = gtk.HBox(homogeneous=False, spacing=5)
        self.main_hbox = main_hbox
        control_vbox = gtk.VBox(homogeneous=False, spacing=5)
        self.control_vbox = control_vbox#control_vbox is assumed to be
            #the name of the vbox on the
            #left of the gui

        self.add_controls_above_notebook()
        self.add_notebook()
        self.add_run_test_button()
        self.add_stop_test_button()
        self.add_save_data_button()
        self.add_controls_below_notebook()

        #add the two main vboxes (control_vbox and canvas_vbox) to the hbox:
        main_hbox.pack_start(self.control_vbox, False, False, 0)
        self.add_figure_canvas()

        main_vbox.pack_start(self.main_hbox, False, False, 0)

        self.textview = gtk.TextView()
        self.textbuffer = self.textview.get_buffer()

        self.textbuffer.set_text("This is a test.\n")

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(5)
        main_vbox.pack_start(scrolled_window, False, False, 0)
        scrolled_window.show()

        scrolled_window.add_with_viewport(self.textview)
        self.text_scrollw = scrolled_window
        self.textview.show()

        self.append_to_log('Test 2.')
        self.append_to_log('Test 3.')

        self.window.add(main_vbox)

        #self.window.set_size_request(width, height)

        self.window.set_title(title)
        # and the window
        #self.window.show()
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.show_all()

        


    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    myapp = PSoC_Refrig_gui()
    #myapp.window.resize(400,300)
    gtk.gdk.threads_init()
    myapp.main()
