# Graphics
from tkinter import *
from tkinter import ttk
from collections import namedtuple

import wavplayer

Mapping = namedtuple('Mapping', 'name file background repeat')

config = {
    'f': Mapping('Forest', 'forest.wav', True, True),
    's': Mapping('Storm', 'storm.wav', True, True),
    'd': Mapping('Door', 'door.wav', False, False),
}

class MapWidget(ttk.Frame):

    def __init__(self, parent, key, mapping):
        super().__init__(parent)
        self.parent = parent

        self.key = StringVar()
        self.name = StringVar()
        self.bg = BooleanVar()
        self.repeat = BooleanVar()
        self.file = StringVar()

        self.key_entry = ttk.Entry(self, width=2, textvariable=self.key)
        self.name_entry = ttk.Entry(self, textvariable=self.name)
        self.bg_cb = ttk.Checkbutton(self, text='Background', variable=self.bg)
        self.repeat_cb = ttk.Checkbutton(self, text='Repeat',
                                         variable=self.repeat)
        self.file_entry = ttk.Entry(self, textvariable=self.file)

        self.key_entry.grid(column=0, row=0)
        self.name_entry.grid(column=1, row=0)
        self.bg_cb.grid(column=2, row=0)
        self.repeat_cb.grid(column=3, row=0)
        self.file_entry.grid(column=4, row=0)

        s = ttk.Style()
        s.configure('Map.TEntry', fieldbackground='#0F0')
        #self.columnconfigure(4, weight=1)

        self.key.set(key)
        self.name.set(mapping.name)
        self.bg.set(mapping.background)
        self.repeat.set(mapping.repeat)
        self.file.set(mapping.file)

        self.bind_all(key, self.play)

    def play(self, event):

        self.highlight()
        self.parent.wp.play(self)

    def highlight(self):

        self.name_entry['style'] = 'Map.TEntry'

    def no_highlight(self):

        self.name_entry['style'] = ''


class Application(Tk):

    def __init__(self):
        super().__init__()

        self.wp = wavplayer.Audio()
        self.create_widgets()
        self.bind_all('X', lambda e: self.wp.stop_all())

    def create_widgets(self):

        for i, (k, v) in enumerate(config.items()):
            mw = MapWidget(self, k, v)
            mw.grid(column=0, row=i)


if __name__ == '__main__':
    app = Application()
    app.mainloop()
