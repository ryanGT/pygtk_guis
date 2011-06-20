#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk

import research_gui
import input_generation

from matplotlib.figure import Figure
#from numpy import arange, sin, pi, cos, array, zeros, int64
from numpy import *

# uncomment to select /GTK/GTKAgg/GTKCairo
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
#from matplotlib.backends.backend_gtkcairo import FigureCanvasGTKCairo as FigureCanvas

import SLFR_RTP, controls
import time, copy, os

neg_accel = True

class SFLR_gui(research_gui.base_class):
    def get_test(self):
        return self.test
        
    def run_test(self, widget, data=None):
        print('in the SFLR_gui.run_test method.')
        ind = self.input_notebook.get_current_page()
        print('current page = %i' % ind)
        cur_page = self.input_notebook.pages[ind]
        print('title = %s' % cur_page.title)
        u = cur_page.create_u_vect()
        mytest = self.get_test()#eventually there will be an open or closed-loop radio button
        mytest.Run_Test(u, plot=False)
        mytest.Close_Serial()
        self.plot_results(test=mytest)

        

    def swept_sine_test(self, widget, data=None):
        print('in swept_sine_test')
        self.test.use_accel_fb = False
        stopn = 20000
        amp = 30
        maxf = 10
        
        wp = 18.5*2*pi
        wz = 16.5*2*pi
        zz = 0.1
        zp = 0.5
        
        G_notch = controls.TransferFunction([1,2*wz*zz,wz**2],\
                                            [1,2*wp*zp,wp**2])*(wp**2/wz**2)
        
        kwargs = {'amp':amp, 'minf':0.0, 'maxf':maxf, 'plot':False,\
                  'stopn':stopn, 'plot':False}
                  
        #self.test.Swept_Sine(**kwargs)
        #self.test.Notched_Swept_Sine(G_notch, **kwargs)
        self.test.Close_Serial()
        self.P_control_test = SLFR_RTP.P_control_Test(kp=1.0, neg_accel=neg_accel)
        self.P_control_test.Swept_Sine(**kwargs)
        self.plot_results(test=self.P_control_test, legloc=3)


        

    def _set_vib_supress(self):
        vib_on = self.vib_on_radio.get_active()
        vib_off = self.vib_off_radio.get_active()

        if self.debug > 0:
            print('vib_on = %s' % vib_on)
            print('vib_off = %s' % vib_off)

        if vib_on:
            self.test.Ga_z = self.Ga_z
            self.test.use_accel_fb = True
        else:
            self.test.use_accel_fb = False

        
    def step_test(self, widget, data=None):
        if self.debug > 0:
            print('in step_test')
        #active = self.vib_check.get_active()
        #toggled = self.vib_check.toggled()

        self._set_vib_supress()

        self.test.Reset_Theta()
        self.test.Software_Zero()
        time.sleep(0.05)
        print('self.test.neg_accel = %s' % self.test.neg_accel)
        self.test.Step_Response(amp=200, stopn=1000, plot=False)#, **kwargs)#, step_ind=10, \
##                   off_ind=100, plot=True, fi=1, clear=True, \
##                   legloc=5)

        self.test.Close_Serial()
        self.plot_results()


    def fixed_sine_test(self, widget, data=None):
        freq_text = self.fs_freq_entry.get_text()
        freq = float(freq_text)
        amp_text = self.fs_amp_entry.get_text()
        amp = int(amp_text)
        dur_text = self.fs_dur_entry.get_text()
        dur = int(dur_text)
        print('freq = %0.4f' % freq)
        print('amp = %i' % amp)
        print('dur = %i' % dur)

        self.test.Reset_Theta()
        self.test.Software_Zero()
        time.sleep(0.05)
        self.test.Fixed_Sine(freq=freq, amp=amp, stopn=dur, plot=False)
        self.test.Close_Serial()
        self.plot_results()
        


    def run_ol_test(self, u):
        self.OL_test = SLFR_RTP.OL_Test(neg_accel=neg_accel)
        self.OL_test.Reset_Theta()
        self.OL_test.Run_Test(u, plot=False)
        self.OL_test.Close_Serial()
        self.plot_results(test=self.OL_test)

        
    def system_check(self, widget, data=None):
        stopn = 1000
        u = zeros((stopn), dtype=int64)
        startind = 50
        width = 50
        amp = 100

        u[startind:startind+width] = amp
        ind3 = stopn/2+startind
        ind4 = ind3+width
        u[ind3:ind4] = -amp

        u[-5:] = 0

        self.run_ol_test(u)


    def run_ol_step(self, widget, data=None):
        stopn = int(self.dur_entry.get_text())
        u = zeros((stopn), dtype=int64)
        startind = 50
        amp_text = self.ol_amp_entry.get_text()
        amp = int(amp_text)
        u[startind:] = amp
        self.run_ol_test(u)
        
        
    def return_to_zero(self, widget, data=None):
        self._set_vib_supress()
        self.test.Step_Response(0, plot=False)
        self.test.Close_Serial()
        

    def reset_theta(self, widget, data=None):
        self.test.Reset_Theta()
        self.test.Close_Serial()


    def add_controls_above_notebook(self):
        self.sys_check_button = gtk.Button("System Check")
        sep0 = gtk.HSeparator()
        self.sys_check_button.connect("clicked", self.system_check, None)
        self.control_vbox.pack_start(self.sys_check_button, False)
        self.control_vbox.pack_start(sep0, False)
        

    def add_controls_below_notebook(self):
        # Creates a new button with the label "Hello World".
        self.reset_button = gtk.Button("Reset Theta")
        self.return_button = gtk.Button("Return to 0")


        #self.vib_check = gtk.CheckButton(label="Use Vibration Suppression", \
        #                                 use_underline=False)
        self.vib_on_radio = gtk.RadioButton(None, "On")
        self.vib_off_radio = gtk.RadioButton(self.vib_on_radio, "Off")
        #button.connect("toggled", self.callback, "radio button 2")
        self.vib_off_radio.set_active(True)
        vib_label = gtk.Label("Vibration Suppression")

        sep1 = gtk.HSeparator()
        sep2 = gtk.HSeparator()
        ## sep3 = gtk.HSeparator()
        ## sep4 = gtk.HSeparator()


        #self.button.set_size_request(30, 40)

        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        self.reset_button.connect("clicked", self.reset_theta, None)
        self.return_button.connect("clicked", self.return_to_zero, None)
        

        #self.vbox1 = gtk.VBox(homogeneous=False, spacing=0)
        # This packs the button into the window (a GTK container).
        #self.window.add(self.button)

        # Add system check button to gui
        # Add input generation notebook to gui
        self.control_vbox.pack_start(sep1, False)
        # Add vibration suppression radio to gui
        self.control_vbox.pack_start(vib_label, False)
        self.control_vbox.pack_start(self.vib_on_radio, False)
        self.control_vbox.pack_start(self.vib_off_radio, False)
        self.control_vbox.pack_start(sep2, False)
        self.control_vbox.pack_start(self.reset_button, False)
        self.control_vbox.pack_start(self.return_button, False)
    

    def __init__(self, debug=0):
        attrs = ['uvect','vvect','yvect','avect','thd_hatvect']
        labels = ['u','v','$\\theta$','a','$\\hat{\\theta}_d$']

        research_gui.base_class.__init__(self, title='SFLR GUI v. 2.0', \
                                         debug=debug, \
                                         plot_attrs=attrs, \
                                         plot_labels=labels)
        
        #create control test case
        p = 20.0*2*pi
        z = 5.0*2*pi
        gain = 5.0
        self.Gth = controls.TransferFunction([1,z], [1,p])*gain*(p/z)
        C_opt = array([ 36.49022971, 172.15528440, 15.39673089, \
                        467.22634242, 281.56096177])

        a2,a1,a0,b1,b0 = C_opt
        gain = 1.0
        
        self.Ga = controls.TF([b1,b0],[1,a2,a1,a0])*gain

        self.dt = 1.0/500
        self.Ga_num, self.Ga_den = self.Ga.c2d_tustin(dt=self.dt)
        self.Ga_z = controls.Digital_Compensator(self.Ga_num, self.Ga_den)

        self.test = SLFR_RTP.Motor_Comp_w_accel_fb(self.Gth, Ga=None, stopn=1000, \
                                                   neg_accel=neg_accel)
        self.test.use_accel_fb = False
        


    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    myapp = SFLR_gui()
    #myapp.window.resize(400,300)
    myapp.main()
