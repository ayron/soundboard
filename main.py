# Graphics
from tkinter import *
from tkinter import ttk
from collections import namedtuple
import yaml

import wavplayer


class MapWidget(ttk.Frame):

    def __init__(self, parent, config):
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

        self.key.set(config['key'])
        self.name.set(config['name'])
        self.bg.set(config['bg'])
        self.repeat.set(config['repeat'])
        self.file.set(config['file'])

        self.bind_all(config['key'], self.play)

    def play(self, event):

        self.highlight()
        self.parent.wp.play(self)

    def highlight(self):

        self.name_entry['style'] = 'Map.TEntry'

    def no_highlight(self):

        self.name_entry['style'] = ''

    def get_config(self):

        return {
            'key': self.key.get(),
            'name': self.name.get(),
            'bg': self.bg.get(),
            'repeat': self.repeat.get(),
            'file': self.file.get()
        }

class Application(Tk):

    def __init__(self):
        super().__init__()

        self.config_path = 'config.yaml'
        self.load_config()

        self.wp = wavplayer.Audio()
        self.create_widgets()
        self.bind_all('X', lambda e: self.wp.stop_all())

        self.save_config()

    def create_widgets(self):

        for i, config in enumerate(self.configs):
            mw = MapWidget(self, config)
            mw.grid(column=0, row=i)

    def load_config(self):

        with open(self.config_path, 'r') as f:
            self.configs = yaml.safe_load(f.read())

    def save_config(self):

        print('Saving config')
        configs = [child.get_config() for child in self.winfo_children()]

        with open(self.config_path, 'w') as f:
            f.write(yaml.safe_dump(configs))

if __name__ == '__main__':
    app = Application()
    app.mainloop()
