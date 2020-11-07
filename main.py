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

        #self.columnconfigure(2, weight=1)

        self.key.set(key)
        self.name.set(mapping.name)
        self.bg.set(mapping.background)
        self.repeat.set(mapping.repeat)
        self.file.set(mapping.file)


class Application(Tk):

    def __init__(self):
        super().__init__()

        self.bind_all('<Key>', self.on_key_pressed)

        self.wp = wavplayer.Audio()

        self.create_widgets()

    def create_widgets(self):

        for i, (k, v) in enumerate(config.items()):
            mw = MapWidget(self, k, v)
            mw.grid(column=0, row=i)

    def on_key_pressed(self, event):

        print("pressed", event.char)

        if event.char == 'X':
            # Stop all sounds

             self.wp.stop_all()

        if event.char in config:
            wav_file = config[event.char].file
            self.wp.play(wav_file)


app = Application()
app.mainloop()
