import os
import Tkinter as tk
import ttk
import pafy
import re
import threading
import logging
import platform
import ConfigParser
from pydub import AudioSegment
from settings import YtSettings
from tkFileDialog import askdirectory
import tkMessageBox
from dl_location import dl_loc

logging.basicConfig(level=logging.DEBUG,
                    filename='ytdl.log',
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='w')
logging.getLogger(__name__)

N = tk.N
S = tk.S
E = tk.E
W = tk.W
END = tk.END

new = YtSettings()


# Linux - additional setting needs to be added to locate ffmpeg.
if platform.system() == 'Linux':
    print('l')
    AudioSegment.converter = "/home/dev/Apps/ffmpeg-git-20150826-64bit-static/ffmpeg"


class Application(tk.Frame):
    """
    GUI for searching YouTube Data API for video URL's. Downloads video and
    mp3 file to user specified location
    """

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initialize()
        self.search_type = "video"

    def initialize(self):
        self.search_frame = tk.LabelFrame(self.parent, bg='gray93',
                                          text="search", padx=9, pady=10)
        self.results_frame = tk.LabelFrame(self.parent, bg='gray93',
                                           text="results", padx=17, pady=10)
        self.choice_dl = tk.LabelFrame(self.parent, bg='gray93',
                                       text="download", padx=5, pady=15)
        self.choice_btns = tk.Frame(self.choice_dl, bg='gray93', padx=10,
                                    pady=15)

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
        self.filemenu = tk.Menu(self.menubar, tearoff=0, )
        root.config(menu=self.menubar)

        # File
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label='Settings',
                                  command=self.create_settings)

    def create_widgets(self):
        self.s = ttk.Style()
        self.s.theme_use('clam')

        self.search_entry = ttk.Entry(self.search_frame, width=72,
                                      textvariable=self.usr_search)
        self.search_entry.bind('<Return>', self.start_search)
        self.search_btn = ttk.Button(self.search_frame, text="search",
                                     command=self.collect_and_populate_results,
                                     style='self.s.TButton')

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
        self.tree.heading("Items", text="Duration",
                          command=lambda: self.treeview_sort(
                              self.tree, "Items", False))

        self.tree_scrollbar = ttk.Scrollbar(self.results_frame,
                                            command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Dl
        self.display_choice = tk.Text(self.choice_dl, x=0, y=50, width=80,
                                      height=2, wrap=tk.WORD)
        self.progbar = ttk.Progressbar(self.parent, orient='horizontal',
                                       length=200, mode='indeterminate')

        self.download_item = ttk.Button(self.choice_btns, text="Video",
                                        command=lambda:
                                        self.download_video_callback())
        self.mp3_btn = ttk.Button(self.choice_btns, text="Mp3",
                                  command=lambda: self.download_ogg_callback())
        self.dl_status = tk.Label(self.parent, textvariable=self.state,
                                  bd=1, relief=tk.SUNKEN, anchor=W,
                                  bg='#424242', fg='#ffffff', pady=3)
        self.choice_dl.grid_columnconfigure(0, weight=1)

    def create_settings(self):
        self.app_settings = tk.Toplevel(self.parent, width=120,
                                        height=50,
                                        bg='gray93',
                                        padx=10, pady=10)
        self.main_settings = tk.Frame(self.app_settings,
                                      bg='gray93', padx=10,
                                      pady=20)
        self.setting_btns = tk.Frame(self.app_settings, bg='gray93')
        self.main_settings.grid(row=0)
        self.setting_btns.grid(row=1, sticky=S + E)

        self.location_label = ttk.Label(self.main_settings, text='Current '
                                                                 'download '
                                                                 'location: ')
        self.location_display = tk.Label(self.main_settings, width=60,
                                         textvariable=self.download_loc_display)
        self.location_change = ttk.Button(self.main_settings, text='Change',
                                          command=self.set_directory)

        self.max_result_lbl = ttk.Label(self.main_settings, text='Number of '
                                                                 'results (Max '
                                                                 '50): ')
        self.max_number = tk.Spinbox(self.main_settings, from_=1, to=50,
                                     width=10)
        self.save_settings = ttk.Button(self.setting_btns, text='Save',
                                        command=self.set_search_max)
        self.cancel_settings = ttk.Button(self.setting_btns, text='Cancel',
                                          command=self.app_settings.destroy)

        self.location_label.grid(row=0, column=0, padx=2)
        self.location_display.grid(row=0, column=1, padx=2)
        self.location_change.grid(row=0, column=2, padx=2)
        self.max_result_lbl.grid(row=1, column=0)
        self.max_number.grid(row=1, column=1)
        self.cancel_settings.grid(row=0, column=0, sticky=E, padx=2)
        self.save_settings.grid(row=0, column=1, sticky=E, padx=2)

    def grid_widgets(self):
        self.search_entry.grid(row=0, column=0)
        self.search_btn.grid(row=0, column=2)
        self.tree.grid(row=0, column=0)
        self.tree_scrollbar.grid(row=0, column=1, sticky=N + S)
        self.display_choice.grid(row=0, column=0)
        self.download_item.grid(row=0, column=0, pady=2)
        self.mp3_btn.grid(row=1, column=0, pady=2)
        self.dl_status.grid(row=2, column=0, sticky=W + E + S)
        self.progbar.grid(row=3, column=0, sticky=W + S)

    def on_double_click(self, event):
        self.get_user_choice()
        self.display_choice.delete(0.0, END)
        self.display_choice.insert(0.0, "You've chosen: {}".format(
            self.user_choice[0].encode('utf-8')))
        self.choice_id = self.find_user_choice_in_playlist_info()

    def treeview_sort(self, tv, col, reverse):
        """
        Sorts treeview listing in alphabetical order
        """
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            tv.move(k, '', index)

        # reverse sort next time
        tv.heading(col, command=lambda: self.treeview_sort(tv, col,
                                                           not reverse))

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
        self.search_entry = self.usr_search.get().replace(" ", "+")
        self.res_list = self.get_result_list()
        return self.res_list

    def get_result_list(self):
        """
        Sends search request to YouTube Data api v3.
        Returns search results as list
        """
        self.result_command = new.yt.search().list(part="snippet",
                                                   q=self.search_entry,
                                                   type=self.search_type,
                                                   maxResults=new.DEFAULT)
        self.result = self.result_command.execute()
        return self.result

    def get_title_duration(self, item):
        """
        Used in populate_tree_view() iteration to collect video duration based
        on the video ID
        """
        duration_call = new.yt.videos().list(part="contentDetails",
                                             id=item['id']['videoId'])
        self.duration_call = duration_call.execute()

    def populate_tree_view(self, search_results):
        """
        Displays search results from the data api.
        Collects title, ID and duration details of each title
        """

        def populate_callback():
            count = 1
            self.playlist_info = []
            self.clear_tree()
            for item in search_results['items']:
                self.get_title_duration(item)
                self.playlist_info.append((item['snippet']['title'],
                                           item['id']['videoId'],
                                           self.duration_call['items'][0][
                                               'contentDetails'][
                                               'duration'].encode('utf-8')))
                m = re.search(r'(\d+\w+)', self.playlist_info[count - 1][2])
                self.tree.insert("", '1', text=str(" "),
                                 values=(item['snippet']['title'],
                                         m.group()),
                                 tags="v_")
                count += 1

        p = threading.Thread(name="Treeview", target=populate_callback)
        p.start()

    def start_search(self, event):
        self.collect_and_populate_results()

    def collect_and_populate_results(self):
        self.r = self.collect_search_result()
        self.populate_tree_view(self.r)

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
        self.state.set('Preparing download please wait')
        self.progbar.start()

        def callback():
            try:
                self.check_download_video_folder()
                self.p = pafy.new(item_id, size=True)
                self.video = self.p.getbest(preftype="mp4")
                self.state.set("Downloading video...")
                self.video.download(filepath=self.video_location,
                                    quiet=True,
                                    callback=self.progress_callback,
                                    meta=True)
            except Exception as e:
                print(e)
                self.missing_folder_warning()

        t = threading.Thread(name='vid_download', target=callback)
        t.start()

    def progress_callback(self, total, recvd, ratio, rate, eta):
        self.update_idletasks()
        if recvd == total:
            self.progbar.stop()
            self.state.set('Download complete')

    def download_ogg(self, item_id):
        """
        Downloads ogg file to a temporary directory to be converted to mp3
        """
        self.state.set('Preparing download please wait')
        self.progbar.start()

        def callback():
            try:
                self.check_audio_download_folder()
                logging.info('audio folder confirmed')
                self.audio = pafy.new(item_id)
                logging.info('pafy object created')
                self.ogg = self.audio.getbestaudio(preftype="ogg")
                logging.info('pafy audio chosen')
                self.state.set('Downloading audio')
                self.ogg.download(filepath=self.temp_file,
                                  callback=self.progress_callback)
                # meta=True)
                self.state.set("Converting to mp3")
                self.convert_to_mp3()
                if os.path.isfile(self.audio_location + '{}.mp3'.format(
                        self.ogg.title.encode('utf-8'))):
                    self.progbar.stop()
                    self.state.set("Conversion complete")
            except AttributeError:
                self.state.set('Download stopped')
                tkMessageBox.showerror(title='Error', message='Unable to '
                                                              'download audio')
            except OSError:
                self.state.set('Download stopped')
                self.missing_folder_warning()
            except Exception, e:
                logging.error('Error: ', exc_info=True)

        t_ogg = threading.Thread(name='ogg_download', target=callback)
        t_ogg.start()

    def convert_to_mp3(self):
        """Converts .ogg file in temp directory to mp3"""
        try:
            self.progbar.start()
            self.fname = self.ogg.filename.encode('utf-8')
            self.working_file = self.temp_file + self.fname
            self.song = AudioSegment.from_file(self.working_file)
            self.song.export(self.audio_location + '{}.mp3'.format(
                self.ogg.title.encode('utf-8')), format="mp3")
            os.remove(self.working_file)
        except:
            logging.error('>: ', exc_info=True)

    def set_directory(self):
        """
        User selects directory they wish to download to.
        This function will set the download location to the chosen
        destination and write the location into a settings file.
        """
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
        try:
            if self.download_dir:
                self.video_location = self.download_dir + 'Videos/'
            if not os.path.exists(self.video_location):
                os.mkdir(self.video_location)
        except:
            raise Exception

    def check_audio_download_folder(self):
        """
        Checks for separate audio folder in download location. Creates
        one if none is present
        """
        if self.download_dir:
            self.audio_location = self.download_dir + 'Audio/'
            self.temp_file = self.download_dir + 'temp/'
        try:
            if not os.path.exists(self.audio_location):
                os.mkdir(self.audio_location)
            if not os.path.exists(self.temp_file):
                os.mkdir(self.temp_file)
        except:
            raise

    def download_video_callback(self):
        try:
            self.download_video(self.choice_id)
        except AttributeError:
            self.missing_id_warning()

    def download_ogg_callback(self):
        try:
            self.download_ogg(self.choice_id)
        except AttributeError:
            self.missing_id_warning()

    def missing_folder_warning(self):
        tkMessageBox.showwarning(title='Missing Download folder',
                                 message='Please choose a download '
                                         'folder in File > Settings')

    def missing_id_warning(self):
        tkMessageBox.showwarning(title='No video ID', message="Select a "
                                                              "video "
                                                              "from the "
                                                              "list first")

    def set_search_max(self):
        """
        Checks search result choice is between 1 and 50.
        Sets this amount temporarily to the search query in the YTSettings
        class.
        """
        try:
            self.a = int(self.max_number.get())
            if self.a > 0:
                if self.a < 51:
                    new.DEFAULT = self.a
                else:
                    raise ValueError
            else:
                raise ValueError
            print(self.a)
        except ValueError:
            tkMessageBox.showwarning(title='Out of range',
                                     message='Choose a search range '
                                             'between 1 and 50')


root = tk.Tk()
root.title('YT to mp3')
root.update()
root.minsize(root.winfo_width(), root.winfo_height())
app = Application(root)
app.parent.configure(background='#555555')

root.mainloop()
