#!/usr/bin/env python3

from tkinter import *
from tkinter import ttk, filedialog, simpledialog
from collections import namedtuple
import yaml
import sys

import wavplayer


def get_config(tree, row):

    return {
        'key': tree.set(row, 'key'),
        'name': tree.set(row, 'name'),
        'bg': tree.set(row, 'bg'),
        'repeat': tree.set(row, 'repeat'),
        'delay': tree.set(row, 'delay'),
        'file': tree.set(row, 'path')
    }


class Application(Tk):

    def __init__(self, config_path):
        super().__init__()

        self.config_path = config_path
        self.load_config()

        self.wp = wavplayer.Audio()
        self.create_widgets()

        # Controls
        self.bind_all('S', lambda e: self.wp.stop_all())
        self.bind_all('A', self.add_track)
        self.bind_all('D', self.delete_track)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):

        self.save_config()
        self.destroy()

    def create_widgets(self):

        tree = ttk.Treeview(self, show='headings',
                columns=('key', 'name', 'repeat', 'bg', 'delay', 'path'))

        tree.column('key', width=35, stretch=False)
        tree.heading('key', text='Key')

        tree.column('name', width=200, stretch=False)
        tree.heading('name', text='Name')

        tree.column('repeat', width=40, stretch=False)
        tree.heading('repeat', text='R')

        tree.column('bg', width=40, stretch=False)
        tree.heading('bg', text='BG')

        tree.column('delay', width=60, stretch=False)
        tree.heading('delay', text='Delay (s)')

        #tree.column('path')
        tree.heading('path', text='Path')

        tree.grid(column=0, row=0, sticky=N+S+E+W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        tree.bind('<Double-Button-1>', self.on_double_click)

        self.tree = tree
        tree.focus_set()

        for i, config in enumerate(self.configs):

            row_id = tree.insert('', 'end',
                    values=(
                        config['key'],
                        config['name'],
                        config['repeat'],
                        config['bg'],
                        config['delay'],
                        config['file']))

            if config['key']:
                tree.bind(config['key'],
                          lambda e, row_id=row_id: self.play(row_id))

        tree.tag_configure('playing', background='#91ff9e')

    def add_track(self, event):

        row_id = self.tree.insert('', 'end',
                values=('', 'New Track', '', '', '', ''))

    def delete_track(self, event):

        selected = self.tree.selection()
        self.tree.delete(*selected)

    def play(self, row_id):

        self.tree.item(row_id, tags='playing')
        self.wp.play(self.tree, row_id)

    def on_double_click(self, event):

        column = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)

        print(column, row)
        if row and column:

            if column == '#3' or column == '#4':

                if self.tree.set(row, column) == '':
                    self.tree.set(row, column, 'x')
                else:
                    self.tree.set(row, column, '')

            elif column == '#6':

                path = filedialog.askopenfilename(
                    title='Select WAV file',
                    filetypes=[('WAVE', '*.wav')])
                self.tree.set(row, column, path)

            elif column == '#2':

                answer = simpledialog.askstring(
                            "Enter name", "Enter a name for the track",
                            parent=self)

                self.tree.set(row, column, answer)

            elif column == '#5':

                answer = simpledialog.askfloat(
                            "Enter float", "Enter a start delay for the track (s)",
                            parent=self)

                self.tree.set(row, column, answer)

            elif column == '#1':

                new_key = simpledialog.askstring(
                            "Enter key", "Enter a key sequence for the track",
                            parent=self)

                old_key = self.tree.set(row, column)
                self.tree.set(row, column, new_key)

                if old_key:
                    self.tree.unbind(old_key)
                self.tree.bind(new_key, lambda e, row=row: self.play(row))

            else:
                print('Column not handled')

    def load_config(self):

        try:
            with open(self.config_path, 'r') as f:
                self.configs = yaml.safe_load(f.read())
        except FileNotFoundError:
            self.configs = []

    def save_config(self):

        print('Saving config')
        configs = [get_config(self.tree, row)
                   for row in self.tree.get_children()]

        with open(self.config_path, 'w') as f:
            f.write(yaml.safe_dump(configs))


if __name__ == '__main__':

    print('Usage: python3 {} [config.yaml]'.format(sys.argv[0]))
    print('')
    print('Keyboard controls:')
    print(' A: Add a new track')
    print(' D: Delete selected tracks')
    print(' S: Stop all tracks')
    print('')

    if len(sys.argv) == 2:
        config_path = sys.argv[1]
    elif len(sys.argv) == 1:
        config_path = 'config.yaml'

    app = Application(config_path)
    app.mainloop()
