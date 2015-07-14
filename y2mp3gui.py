from apiclient.discovery import build
from apiclient.errors import HttpError
import os
import logging
import Tkinter as tk
import ttk
import pafy
from pydub import AudioSegment
from gogetmp3 import YtData

N = tk.N
S = tk.S
E = tk.E
W = tk.W
END = tk.END

new = YtData()


def print_uri():
    """Tests search output to be directed to data api."""
    search_ent = app.usr_search.get().replace(" ", "+")
    search_type = app.vidtype.get()
    res = new.yt.search().list(part="snippet", q=search_ent, type=search_type,
                               maxResults=new.DEFAULT)
    assert new.DEVELOPER_KEY in res.uri
    print res.uri


def print_uri_from_return(event):
    """Tests return event"""
    print_uri()


class Application(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.search_frame = tk.LabelFrame(self.parent, bg='gray93',
                                          text="search")
        self.results_frame = tk.LabelFrame(self.parent, bg='gray93',
                                           text="results")

        self.search_frame.grid(row=0, column=0)
        self.results_frame.grid(row=1, column=0)

        self.create_variables()
        self.create_menubar()
        self.create_widgets()
        self.grid_widgets()

    def create_variables(self):
        self.usr_search = tk.StringVar()
        self.vidtype = tk.StringVar(self.search_frame)
        self.type_options = ["Select type", "video", "playlist"]
        self.vidtype.set(self.type_options[1])

    def create_menubar(self):
        pass

    def create_widgets(self):
        self.search_ent = ttk.Entry(self.search_frame, width=50,
                                    textvariable=self.usr_search)
        self.search_ent.bind('<Return>', print_uri_from_return)
        self.type = apply(ttk.OptionMenu, (self.search_frame, self.vidtype) +
                          tuple(self.type_options))
        self.type['width'] = 10
        self.search_btn = ttk.Button(self.search_frame, text="search",
                                     command=print_uri)
        self.tree_columns = ("Name", "Items")
        self.tree = ttk.Treeview(self.results_frame, columns=self.tree_columns,
                                 height=15,
                                 selectmode='browse')
        self.tree.column("#0", width=50)
        self.tree.column("Name", width=100)
        self.tree.column("Items", width=500)

        self.tree_scrollbar = ttk.Scrollbar(self.results_frame,
                                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)


    def grid_widgets(self):
        self.search_ent.grid(row=0, column=0)
        self.type.grid(row=0, column=1)
        self.search_btn.grid(row=0, column=2)
        self.tree.grid(row=0, column=0)
        self.tree_scrollbar.grid(row=0, column=1, sticky=N+S)

    






root = tk.Tk()
root.title('YT to mp3')
root.update()
root.minsize(root.winfo_width(), root.winfo_height())

app = Application(root)

root.mainloop()
