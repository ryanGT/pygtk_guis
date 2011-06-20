"""This module fascillitates the creation of a notebook control used
to specify the input vector for an open or closed-loop dynamic system
test.  Different pages of the notebook allow the user to specify
inputs for swept-sine, fixed-sine, step, or impulse tests."""

import pygtk
pygtk.require('2.0')
import gtk

#default params for packing and configuring
Entry_width = 50
max_len = 10
myspace = 5
pack_args_pad = (False, False, 5)
args_no_pad = (False, False, 0)


class input_page(gtk.VBox):
    def __init__(self, title, labels, attrs, defaults):
        gtk.VBox(self, homogeneous=False, spacing=myspace)
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

        
    
    def _create_u_zeros(self, dtype=float64):
        dur_text = self.dur.get_text()
        duration = int(dur_text)
        u = zeros(duration, dtype=dtype)
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
                 defaults=['50', '50', '1000'])


    def create_u_vect(self):
        u = self._create_u_zeros()
        start = self._get_int('start')
        amp = self._get_int('amp')
        u[start:] = amp
        return u

        
class input_gen_notebool(gtk.Notebook):
    def _create_pages(self):
        class_list = [swept_sine_page]
        for cur_class in class_list:
            page = cur_class()
            self.append_page(page, page.title)

        
    def __init__(self, *args, **kwargs):
        gtk.Notebook.__init__(self, *arg, **kwargs)
        self.set_tab_pos(gtk.POS_TOP)
        self.show()

    
