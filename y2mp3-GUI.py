import Tkinter as tk
import ttk

N = tk.N
S = tk.S
E = tk.E
W = tk.W
END = tk.END


class Application(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.search_frame = tk.LabelFrame(self.parent, bg='gray93', text="search")

        self.search_frame.grid(row=0, column=0)

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
        self.search_ent = ttk.Entry(self.search_frame, width=50)
        self.type = apply(ttk.OptionMenu, (self.search_frame, self.vidtype) + tuple(self.type_options))
        self.type['width'] = 10
        self.search_btn = ttk.Button(self.search_frame, text="search")

    def grid_widgets(self):
        self.search_ent.grid(row=0, column=0)
        self.type.grid(row=0, column=1)
        self.search_btn.grid(row=0, column=2)


root = tk.Tk()
root.title('YT to mp3')
root.update()
root.minsize(root.winfo_width(), root.winfo_height())

app = Application(root)

root.mainloop()
