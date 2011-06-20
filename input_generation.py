"""This module fascillitates the creation of a notebook control used
to specify the input vector for an open or closed-loop dynamic system
test.  Different pages of the notebook allow the user to specify
inputs for swept-sine, fixed-sine, step, or impulse tests."""

import pygtk
pygtk.require('2.0')
import gtk

import numpy

#default params for packing and configuring
Entry_width = 50
max_len = 10
myspace = 5
pack_args_pad = (False, False, 5)
args_no_pad = (False, False, 0)


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
        


class swept_sine_page(input_page):
    def __init__(self, title='Swept Sine', \
                 labels=['amp.', 'start ind', 'dur.'], \
                 attrs=['amp', 'start', 'dur',], \
                 defaults=['50', '50', '1000']):
        input_page.__init__(self, title=title, \
                            labels=labels, \
                            attrs=attrs, \
                            defaults=defaults)


    def create_u_vect(self):
        u = self._create_u_zeros()
        start = self._get_int('start')
        amp = self._get_int('amp')
        u[start:] = amp
        return u


class impulse_page(input_page):
    def __init__(self, title='Impulse', \
                 labels=['amp.', 'start ind', 'pulse width', 'dur.'], \
                 attrs=['amp', 'start', 'width', 'dur',], \
                 defaults=['50', '50', '20', '1000']):
        input_page.__init__(self, title=title, \
                            labels=labels, \
                            attrs=attrs, \
                            defaults=defaults)


    def create_u_vect(self):
        u = self._create_u_zeros()
        start = self._get_int('start')
        width = self._get_int('width')
        amp = self._get_int('amp')
        dur = self._get_int('dur')
        stop_ind = start+width
        assert stop_ind < dur, "You have chosen an invalid combination of " + \
                               "pulse width, start index, and test duration. \n" + \
                               "stop_ind must be less than duration; stop_ind = start_ind + width."
        u[start:start_ind] = amp
        return u

        
class input_gen_notebook(gtk.Notebook):
    def _create_pages(self):
        class_list = [swept_sine_page, impulse_page]
        attr_list = ['swept_sine_page', 'impulse_page']
        for cur_class, attr in zip(class_list, attr_list):
            page = cur_class()
            setattr(self, attr, page)
            tab_label = gtk.Label(page.title)
            self.append_page(page, tab_label)

        
    def __init__(self, *args, **kwargs):
        gtk.Notebook.__init__(self, *args, **kwargs)
        self.set_tab_pos(gtk.POS_TOP)
        self.show()
        self._create_pages()

    
