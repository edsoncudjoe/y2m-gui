import os
import Tkinter as tk
import ttk
import pafy
from pydub import AudioSegment
from settings import YtSettings
from tkFileDialog import askdirectory
from dl_location import dl_loc

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
        self.search_type = "video"

    def initialize(self):
        self.search_frame = tk.LabelFrame(self.parent, bg='gray93',
                                          text="search", padx=20, pady=20)
        self.results_frame = tk.LabelFrame(self.parent, bg='gray93',
                                           text="results", padx=20, pady=20)
        self.choice_dl = tk.LabelFrame(self.parent, bg='gray93',
                                       text="download", padx=20, pady=20)
        self.choice_btns = tk.Frame(self.choice_dl, bg='gray93', padx=10,
                                    pady=10)

        self.search_frame.grid(row=0, column=0)
        self.results_frame.grid(row=1, column=0)
        self.choice_dl.grid(row=2, column=0)
        self.choice_btns.grid(row=0, column=1, rowspan=2)

        self.create_variables()
        self.create_menubar()
        self.create_widgets()
        self.grid_widgets()

    def create_variables(self):
        self.usr_search = tk.StringVar()
        self.state = tk.StringVar()
        self.download_dir = dl_loc
        self.download_loc_display = tk.StringVar()
        self.download_loc_display.set(self.download_dir)

    def create_menubar(self):
        self.menubar = tk.Menu(self.parent)
        self.filemenu = tk.Menu(self.menubar, tearoff=0,)
        root.config(menu=self.menubar)

        # File
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label='Settings',
                                  command=self.create_settings)


    def create_widgets(self):
        self.search_ent = ttk.Entry(self.search_frame, width=72,
                                    textvariable=self.usr_search)
        self.search_ent.bind('<Return>', self.start_search)
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
        self.display_choice = tk.Text(self.choice_dl, x=0, y=50, width=79,
                                      height=2, wrap=tk.WORD)
        self.download_item = ttk.Button(self.choice_btns, text="Video",
                                        command=lambda: self.download_video(
                                            self.choice_id))
        self.mp3_btn = ttk.Button(self.choice_btns, text="Mp3",
                                  command=lambda: self.dl_ogg(
                                      self.choice_id))
        self.dl_status = tk.Label(self.choice_dl, textvariable=self.state,
                                  width=70)

    def create_settings(self):
        self.location_settings = tk.Toplevel(self.parent, width=120,
                                             height=50,
                                             bg='gray93',
                                             padx=10, pady=10)
        self.main_settings = tk.Frame(self.location_settings,
                                      bg='gray93', padx=10,
                                      pady=20)
        self.main_settings.grid()

        self.location_label = ttk.Label(self.main_settings, text='Current '
                                                                 'download '
                                                                 'location: ')
        self.location_display = tk.Label(self.main_settings, width=60,
                                        textvariable=self.download_loc_display)
        self.location_change = ttk.Button(self.main_settings, text='Change',
                                          command=self.set_directory)

        self.location_label.grid(row=0, column=0)
        self.location_display.grid(row=0, column=1)
        self.location_change.grid(row=0, column=2)


    def grid_widgets(self):
        self.search_ent.grid(row=0, column=0)
        self.search_btn.grid(row=0, column=2)
        self.tree.grid(row=0, column=0)
        self.tree_scrollbar.grid(row=0, column=1, sticky=N + S)
        self.display_choice.grid(row=0, column=0)
        self.download_item.grid(row=0, column=0)
        self.mp3_btn.grid(row=1, column=0)
        self.dl_status.grid(row=2, column=0)

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
        for item in search_results['items']:
            self.playlist_info.append((item['snippet']['title'],
                                       item['id']['videoId']))
            self.tree.insert("", '1', text=str(" "),
                             values=(item['snippet']['title'],), tags="v_")
            count += 1

    def start_search(self, event):
        self.collect_and_populate_results()

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
        self.check_download_video_folder()
        self.p = pafy.new(item_id, size=True)
        self.video = self.p.getbest(preftype="mp4")
        self.state.set("Downloading video...")
        self.video.download(filepath=self.video_location,
                            quiet=True,
                            callback=self.progress_callback,
                            meta=True)

    def progress_callback(self, total, recvd, ratio, rate, eta):
        self.update_idletasks()
        if recvd == total:
            self.state.set('Download complete')

    def dl_ogg(self, item_id):
        self.check_audio_download_folder()
        self.audio = pafy.new(item_id)
        self.ogg = self.audio.getbestaudio(preftype="ogg")
        self.ogg.download(filepath=self.temp_file,
                          callback=self.progress_callback,
                          meta=True)
        self.state.set("Starting conversion")
        self.convert_to_mp3()
        if os.path.isfile(self.audio_location + '{}.mp3'.format(
                self.ogg.title)):
            self.state.set("Conversion complete")

    def convert_to_mp3(self):
        self.fname = self.ogg.filename.encode('utf-8')
        self.working_file = self.temp_file + self.fname
        self.song = AudioSegment.from_file(self.working_file)
        self.song.export(self.audio_location + '{}.mp3'.format(
            self.ogg.title), format="mp3")
        os.remove(self.working_file)

    def set_directory(self):
        print('Current dl directory: {}'.format(self.download_dir))
        user_dir = askdirectory()
        self.download_dir = user_dir + '/YT2Mp3/'
        os.mkdir(self.download_dir)
        self.download_loc_display.set(self.download_dir)
        with open('dl_location.py', 'w') as set_download:
            set_download.write('dl_loc = \'{}\''.format(
                self.download_dir))

    def check_download_video_folder(self):
        """
        Checks for separate video folder in download location. Creates
        one if none is present
        """
        self.video_location = self.download_dir + 'Videos/'
        if not os.path.exists(self.video_location):
            os.mkdir(self.video_location)
       
    def check_audio_download_folder(self):
        self.audio_location = self.download_dir + 'Audio/'
        self.temp_file = self.download_dir + 'temp/'
        if not os.path.exists(self.audio_location):
            os.mkdir(self.audio_location)
        print(self.temp_file)
        if not os.path.exists(self.temp_file):
            os.mkdir(self.temp_file)

root = tk.Tk()
root.title('YT to mp3')
root.update()
root.minsize(root.winfo_width(), root.winfo_height())
# yt = Yt()
app = Application(root)

root.mainloop()
