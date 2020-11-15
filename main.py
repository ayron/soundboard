# Graphics
from tkinter import *
from tkinter import ttk, filedialog, simpledialog
from collections import namedtuple
import yaml

import wavplayer


def get_config(tree, row):

    return {
        'key': tree.set(row, 'key'),
        'name': tree.set(row, 'name'),
        'bg': tree.set(row, 'bg'),
        'repeat': tree.set(row, 'repeat'),
        'file': tree.set(row, 'path')
    }


class Application(Tk):

    def __init__(self):
        super().__init__()

        self.config_path = 'config.yaml'
        self.load_config()

        self.wp = wavplayer.Audio()
        self.create_widgets()
        self.bind_all('X', lambda e: self.wp.stop_all())

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):

        self.save_config()
        self.destroy()

    def create_widgets(self):

        tree = ttk.Treeview(self, show='headings',
                columns=('key', 'name', 'repeat', 'bg', 'path'))

        tree.column('key', width=35, stretch=False)
        tree.heading('key', text='Key')

        tree.column('name', width=200, stretch=False)
        tree.heading('name', text='Name')

        tree.column('repeat', width=40, stretch=False)
        tree.heading('repeat', text='R')

        tree.column('bg', width=40, stretch=False)
        tree.heading('bg', text='BG')

        #tree.column('path')
        tree.heading('path', text='Path')

        tree.grid(column=0, row=0, sticky=N+S+E+W)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        tree.bind('<Double-Button-1>', self.on_double_click)

        self.tree = tree

        for i, config in enumerate(self.configs):

            row_id = tree.insert('', 'end',
                    values=(
                        config['key'],
                        config['name'],
                        config['repeat'],
                        config['bg'],
                        config['file']))

            tree.bind(config['key'], lambda e, row_id=row_id: self.play(row_id))

        tree.tag_configure('playing', background='#91ff9e')

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

            elif column == '#5':

                path = filedialog.askopenfilename(
                    title='Select WAV file',
                    filetypes=[('WAVE', '*.wav')])
                self.tree.set(row, column, path)

            elif column == '#2':

                answer = simpledialog.askstring(
                            "Enter name", "Enter a name for the track",
                            parent=self)

                self.tree.set(row, column, answer)

            elif column == '#1':

                new_key = simpledialog.askstring(
                            "Enter key", "Enter a key sequence for the track",
                            parent=self)

                old_key = self.tree.set(row, column)
                self.tree.set(row, column, new_key)

                self.tree.unbind(old_key)
                self.tree.bind(new_key, lambda e, row=row: self.play(row))

            else:
                print('Column not handled')

    def load_config(self):

        with open(self.config_path, 'r') as f:
            self.configs = yaml.safe_load(f.read())

    def save_config(self):

        print('Saving config')
        configs = [get_config(self.tree, row)
                   for row in self.tree.get_children()]

        with open(self.config_path, 'w') as f:
            f.write(yaml.safe_dump(configs))


if __name__ == '__main__':
    app = Application()
    app.mainloop()
