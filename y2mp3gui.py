from apiclient.discovery import build
from apiclient.errors import HttpError
import os
import logging
import Tkinter as tk
import ttk
import pafy
from pydub import AudioSegment
from settings import YtSettings

N = tk.N
S = tk.S
E = tk.E
W = tk.W
END = tk.END

new = YtSettings()


class Application(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.search_frame = tk.LabelFrame(self.parent, bg='gray93',
                                          text="search")
        self.results_frame = tk.LabelFrame(self.parent, bg='gray93',
                                           text="results")
        self.choice_dl = tk.LabelFrame(self.parent, bg='gray93',
                                       text="download")

        self.search_frame.grid(row=0, column=0)
        self.results_frame.grid(row=1, column=0)
        self.choice_dl.grid(row=2, column=0)

        self.create_variables()
        self.create_menubar()
        self.create_widgets()
        self.grid_widgets()

        self.progress_val = 0
        self.maxbytes = 0

    def create_variables(self):
        self.usr_search = tk.StringVar()
        self.vidtype = tk.StringVar(self.search_frame)
        self.type_options = ["Select type", "video", "playlist"]
        self.vidtype.set(self.type_options[1])
        # self.prog = tk.IntVar()
        self.state = tk.StringVar()

    def create_menubar(self):
        pass

    def create_widgets(self):
        self.search_ent = ttk.Entry(self.search_frame, width=57,
                                    textvariable=self.usr_search)
        self.search_ent.bind('<Return>', self.print_uri)
        self.type = apply(ttk.OptionMenu, (self.search_frame, self.vidtype) +
                          tuple(self.type_options))
        self.type['width'] = 10
        self.search_btn = ttk.Button(self.search_frame, text="search",
                                     command=self.collect_and_populate_results)

        # Tree
        self.tree_columns = ("Name", "Items")
        self.tree = ttk.Treeview(self.results_frame, columns=self.tree_columns,
                                 height=15,
                                 selectmode='browse')
        self.tree.tag_bind("v_", "<Double-1>", self.on_double_click)
        self.tree.tag_bind("pl_", "<Double-1>", self.on_double_click)
        self.tree.column("#0", width=50)
        self.tree.column("Name", width=500)
        self.tree.column("Items", width=100)
        self.tree.heading("Name", text="Name",
                          command=lambda: self.treeview_sort(
                              self.tree, "Name", False))
        self.tree.heading("Items", text="Items",
                          command=lambda: self.treeview_sort(
                              self.tree, "Items", False))

        self.tree_scrollbar = ttk.Scrollbar(self.results_frame,
                                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Dl
        self.display_choice = tk.Text(self.choice_dl, x=0, y=50, width=83,
                                      height=2, wrap=tk.WORD)
        self.download_item = ttk.Button(self.choice_dl, text="D",
                                        command=lambda: self.download_video(self.choice_id))
        #self.progress = ttk.Progressbar(self.choice_dl, orient="horizontal",
        #                                length=300, mode="determinate",
        #                                variable=self.prog)
        self.dl_status = tk.Label(self.choice_dl, textvariable=self.state,
                                  width=80)

    def grid_widgets(self):
        self.search_ent.grid(row=0, column=0)
        self.type.grid(row=0, column=1)
        self.search_btn.grid(row=0, column=2)
        self.tree.grid(row=0, column=0)
        self.tree_scrollbar.grid(row=0, column=1, sticky=N + S)
        self.display_choice.grid(row=0, column=0)
        self.download_item.grid(row=0, column=1)
        self.dl_status.grid(row=1, column=0, columnspan=2)
        # self.progress.grid(row=2, column=0, columnspan=2)

    def on_double_click(self, event):
        self.get_user_choice()
        self.display_choice.delete(0.0, END)
        self.display_choice.insert(0.0, "You've chosen: {}".format(
            self.user_choice[0].encode('utf-8')))
        self.choice_id = self.find_user_choice_in_playlist_info()

    def treeview_sort(self, tv, col, reverse):
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: \
            self.treeview_sort(tv, col, not reverse))

    def print_uri(self):
        """
        Currently unused
        Tests search output to be directed to data api.
        """
        search_ent = self.usr_search.get().replace(" ", "+")
        search_type = self.vidtype.get()
        res = new.yt.search().list(part="snippet", q=search_ent,
                                   type=search_type,
                                   maxResults=new.DEFAULT)
        assert new.DEVELOPER_KEY in res.uri
        print res.uri

    def collect_search_result(self):
        """"Collects user entrys as variables"""
        self.search_ent = self.usr_search.get().replace(" ", "+")
        self.search_type = self.vidtype.get()
        self.res_list = self.get_result_list()
        return self.res_list

    def get_result_list(self):
        """
        Sends search request to YouTube Data api v3.
        Returns search results as list
        """
        self.result_command = new.yt.search().list(part="snippet",
                                                   q=self.search_ent,
                                                   type=self.search_type,
                                                   maxResults=new.DEFAULT)
        self.result = self.result_command.execute()
        return self.result

    def populate_treeview(self, search_results):
        """Displays search results from the data api."""
        count = 1
        self.playlist_info = []
        self.clear_tree()
        if self.search_type == "playlist":
            try:
                for item in search_results['items']:
                    self.pl_data = new.yt.playlists().list(
                        part="contentDetails",
                        id=item['id']['playlistId']).execute()

                    for p in self.pl_data['items']:
                        self.playlist_info.append(
                            (item['snippet']['title'],
                             item['id']['playlistId'],
                             p['contentDetails']['itemCount']))

                        self.tree.insert("", 'end', text=str(" "),
                                         values=(
                                             item['snippet']['title'],
                                             str(p['contentDetails'][
                                                     'itemCount']) +
                                             " videos"), tags="pl_")
                    count += 1
            except Exception, e:
                print(e)
        else:
            for item in search_results['items']:
                self.playlist_info.append((item['snippet']['title'],
                                           item['id']['videoId']))
                self.tree.insert("", '1', text=str(" "),
                                 values=(item['snippet']['title'],), tags="v_")
                count += 1

    def collect_and_populate_results(self):
        self.r = self.collect_search_result()
        self.populate_treeview(self.r)

    def clear_tree(self):
        for i in self.tree.get_children():
            app.tree.delete(i)

    def get_user_choice(self):
        item = self.tree.focus()
        self.user_choice = self.tree.item(item, option='values')
        return self.user_choice

    def find_user_choice_in_playlist_info(self):
        for i in self.playlist_info:
            if i[0] == self.user_choice[0]:
                return i[1]

    def download_video(self, item_id):
        self.p = pafy.new(item_id, size=True)
        self.video = self.p.getbest(preftype="mp4")
        self.state.set("Downloading video...")
        self.video.download(filepath="./Video/",
                            quiet=True,
                            callback=self.progress_callback,
                            meta=True)

    def progress_callback(self, total, recvd, ratio, rate, eta):
        self.update_idletasks()
        if recvd == total:
            self.state.set("Download complete.")
        #self.progress["maximum"] = total
        #self.progress_val += recvd
        #self.progress['value'] = self.progress_val
        #self.progress.update_idletasks()

    def get_id_and_download(self):
        """currently unused"""
        # self.choice_id = self.find_user_choice_in_playlist_info()
        self.download_video(self.choice_id)


# set up dl from vid id
# setup dl from playlist
# tidy up


# if __name__ == '__main__':
root = tk.Tk()
root.title('YT to mp3')
root.update()
root.minsize(root.winfo_width(), root.winfo_height())
# yt = Yt()
app = Application(root)

root.mainloop()
