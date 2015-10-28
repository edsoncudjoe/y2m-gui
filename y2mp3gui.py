import os
import Tkinter as tk
import ttk
import pafy
import re
import threading
import logging
import platform
import ConfigParser
from settings import YtSettings
from tkFileDialog import askdirectory
from converter import Converter
import tkMessageBox

logging.basicConfig(level=logging.DEBUG,
                    filename='y2m.log',
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='w')
logging.getLogger(__name__)

Settings = ConfigParser.ConfigParser()
Parse = ConfigParser.SafeConfigParser()

N = tk.N
S = tk.S
E = tk.E
W = tk.W
END = tk.END

new = YtSettings()

if platform.system() == 'Darwin':
    fc = Converter(ffmpeg_path='/usr/local/bin/ffmpeg',
                   ffprobe_path='/usr/local/bin/ffprobe')
else:
    fc = Converter()

fc_options = {
    'format': 'mp3',
    'audio': {
        'codec': 'mp3',
        'bitrate': '44100',
        'channels': 2
    }
}


class Setting(tk.Frame):
    """Settings window"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.dl_loc = None
        try:
            Parse.readfp(open('./config.ini'))
            self.dl_loc = Parse.get('download', 'directory')
        except IOError:
            logging.error('Unable to locate config file', exc_info=True)
            tkMessageBox.showwarning('Warning', 'no directory saved')
        except Exception as e:
            print(e)

        self.download_dir = self.dl_loc
        self.ffmpeg_path = tk.StringVar()
        self.ffprobe_path = tk.StringVar()
        self.download_loc_display = tk.StringVar()
        self.default_result_amt = tk.StringVar()
        self.default_result_amt.set('25')
        self.download_loc_display.set(self.download_dir)

        self.settings_win = tk.Toplevel(self.parent, width=120,
                                        height=50,
                                        bg='gray93',
                                        padx=10, pady=10)

        self.main_settings_fr = tk.Frame(self.settings_win,
                                      bg='gray93', padx=10,
                                      pady=20)
        self.settings_win_btns = tk.Frame(self.settings_win, bg='gray93')
        self.main_settings_fr.grid(row=0)
        self.settings_win_btns.grid(row=1, sticky=S + E)

        self.location_label = ttk.Label(self.main_settings_fr, text='Current '
                                                                 'download '
                                                                 'location: ')
        self.location_display = tk.Label(self.main_settings_fr, width=60,
                                         textvariable=self.download_loc_display)
        self.location_change = ttk.Button(self.main_settings_fr, text='Change',
                                          command=self.set_directory)
        self.ffmpeg_path_lbl = ttk.Label(self.main_settings_fr, text='FFMpeg '
                                                                'location: ')
        self.ffmpeg_path_entry = ttk.Entry(self.main_settings_fr,
                                           textvariable=self.ffmpeg_path,
                                           width=30)
        self.ffprobe_path_lbl = ttk.Label(self.main_settings_fr,
                                          text='FFprobe '
                                                                 'location: ')
        self.ffprobe_path_entry = ttk.Entry(self.main_settings_fr,
                                            textvariable=self.ffprobe_path,
                                            width=30)
        self.max_result_lbl = ttk.Label(self.main_settings_fr, text='Number of '
                                                                 'results (Max '
                                                                 '50): ')
        self.max_number = tk.Spinbox(self.main_settings_fr, from_=1, to=50,
                                     textvariable=self.default_result_amt,
                                     width=10)
        self.save_settings = ttk.Button(self.settings_win_btns, text='Apply',
                                        command=self.set_search_max)
        self.cancel_settings = ttk.Button(self.settings_win_btns, text='Cancel',
                                          command=self.settings_win.destroy)
        self.close_settings = ttk.Button(self.settings_win_btns, text='OK',
                                         command=self.settings_win.destroy)

        self.location_label.grid(row=0, column=0, padx=2)
        self.location_display.grid(row=0, column=1, padx=2)
        self.location_change.grid(row=0, column=2, padx=2)
        self.max_result_lbl.grid(row=1, column=0)
        self.max_number.grid(row=1, column=1)
        self.ffmpeg_path_lbl.grid(row=2, column=0)
        self.ffmpeg_path_entry.grid(row=2, column=1)
        self.ffprobe_path_lbl.grid(row=3, column=0)
        self.ffprobe_path_entry.grid(row=3, column=1)
        self.cancel_settings.grid(row=0, column=0, sticky=E, padx=2)
        self.save_settings.grid(row=0, column=1, sticky=E, padx=2)
        self.close_settings.grid(row=0, column=2, sticky=E, padx=2)

    def set_directory(self):
        """
        User selects directory they wish to download to.
        This function will set the download location to the chosen
        destination and write the location into a settings file.
        """
        user_dir = askdirectory()
        try:
            self.download_dir = user_dir + '/YT2Mp3/'
            os.mkdir(self.download_dir)
            self.download_loc_display.set(self.download_dir)

        # ConfigParser
            dldir_conf = open('./config.ini', 'w')
            Settings.add_section('download')
            Settings.set('download', 'directory', self.download_dir)
            Settings.write(dldir_conf)
            dldir_conf.close()

            tkMessageBox.showinfo('Download directory saved', 'Please restart the '
                                                 'application for the '
                                                 'directory settings to take '
                                                          'effect.')
        except OSError:
            pass

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


class MenuBar(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.menubar = tk.Menu(self.parent)
        self.filemenu = tk.Menu(self.menubar, tearoff=0, )
        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        root.config(menu=self.menubar)

        # File
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label='Settings', command=self.call_settings)
        self.filemenu.add_separator()
        self.filemenu.add_command(label='Quit', command=self.exit_app)

        # Help
        self.menubar.add_cascade(label="Help", menu=self.helpmenu)
        self.helpmenu.add_command(label="About", command=self.about)

    def about(self):
        tkMessageBox.showinfo("YTdl2mp3 1.0.0",
                          "\nYoutube Downloader\n"
                          "\nCreated by E.Cudjoe"
                          "\nVersion 1.0.0"
                          "\nhttps://github.com/edsoncudjoe")

    def call_settings(self):
        self.app_settings = Setting(self)

    def exit_app(self):
        if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
            root.quit()


class SearchItems(tk.Frame):
    """"""
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        self.search_entry = None
        self.search_type = "video"
        self.usr_search = tk.StringVar()

        self.search_frame = tk.LabelFrame(self.parent,
                                          text="search", padx=2, pady=6,
                                          relief=tk.FLAT, background='#676767',
                                          foreground='#f5f5f5')
        self.search_frame.grid(sticky=N+E+W)
        self.search_frame.columnconfigure(0, weight=1)
        self.search_frame.rowconfigure(0, weight=1)

        self.search_box = ttk.Entry(self.search_frame, width=75,
                                      textvariable=self.usr_search)
        self.search_box.bind('<Return>', self.start_search)
        self.search_btn = ttk.Button(self.search_frame, text="search",
                                     command=self.collect_and_populate_results)

        self.search_box.grid(row=0, column=0, sticky=N+E+W)
        self.search_btn.grid(row=0, column=1, padx=5)

    def start_search(self, event):
        self.collect_and_populate_results()

    def collect_and_populate_results(self):
        r = self.collect_search_result()
        app.result_tree.populate_tree_view(r)

    def collect_search_result(self):
        """"Collects user entrys as variables"""
        self.search_entry = self.usr_search.get().replace(" ", "+")
        res_list = self.get_result_list()
        return res_list

    def get_result_list(self):
        """
        Sends search request to YouTube Data api v3.
        Returns search results as list
        """
        try:
            result_command = new.yt.search().list(part="snippet",
                                                       q=self.search_entry,
                                                       type=self.search_type,
                                                       maxResults=new.DEFAULT)
            result = result_command.execute()
            return result
        except AttributeError:
            tkMessageBox.showerror("Server Error", "I am unable to contact YouTube's Servers"
                                                   "\nPlease check your internet connection")
            logging.error("Unable to contact YouTube servers", exc_info=True)


class ResultTree(tk.Frame):
    """"""
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)

        self.playlist_info = []
        self.choice_id = None
        self.user_choice = None
        self.start_pafy = None

        self.results_frame = tk.LabelFrame(self.parent, bg='#676767',
                                           fg='#f5f5f5',
                                           text="results",
                                           relief=tk.FLAT,
                                           padx=7, pady=2)
        self.results_frame.grid(sticky=N+S+E+W)
        self.results_frame.columnconfigure(0, weight=1)
        self.results_frame.rowconfigure(0, weight=1)

        self.tree_columns = ("Name", "Items")
        self.tree = ttk.Treeview(self.results_frame, columns=self.tree_columns,
                                 height=15,
                                 selectmode='browse')
        self.tree.tag_bind("v_", "<Double-1>", self.on_double_click)
        self.tree.tag_bind("pl_", "<Double-1>", self.on_double_click)
        self.tree.column("#0", width=50)
        self.tree.column("Name", width=522)
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
        spacer = tk.LabelFrame(self.results_frame, text='\n', bg='#676767',
                               relief=tk.FLAT, pady=1)
        self.display_choice = tk.Text(self.results_frame, width=95,
                                      height=5, wrap=tk.WORD, bd=1,
                                      bg='#ffffff', fg='#006600',
                                      relief=tk.SUNKEN)

        self.tree.grid(row=0, column=0, sticky=N+S+E+W)
        self.tree.columnconfigure(0, weight=1)
        self.tree.rowconfigure(0, weight=1)
        self.tree_scrollbar.grid(row=0, column=1, sticky=N + S)
        spacer.grid(row=1, column=0)
        self.display_choice.grid(row=2, column=0, sticky=E+W)

    def on_double_click(self, event):
        self.get_user_choice()
        self.display_choice.delete(0.0, END)
        self.display_choice.insert(0.0, "Title: {} "
                                        "\n\nDescription: {}".format(
            self.user_choice[0].encode('utf-8'),
            self.user_choice[2].encode('utf-8')))

        self.choice_id = self.find_user_choice_in_playlist_info()
        dl_option_thread = threading.Thread(name='download_options',
                                            target=self.get_dl_options,
                                            args=(self.choice_id, ))
        dl_option_thread.start()
        # print self.choice_id

    def get_dl_options(self, clip_id):
        """
        Creates a Pafy instance to collect a list of file formats
        available for download
        """
        def dl_opt_list():
            try:
                app.download_items.state.set("Checking available download "
                                             "options")
                self.start_pafy = pafy.new(clip_id, size=True)
                app.download_items.dl_options = []
                app.download_items.dl_options = [(i, str(i)) for i in
                                                 self.start_pafy.streams]
                app.download_items.refresh_dl_options()
                app.download_items.state.set("Download options loaded")
                # print app.download_items.dl_options
            except AttributeError as e:
                app.download_items.state.set("Internal error getting options")
                logging.error(e)

        get_dl_options = threading.Thread(name='get_options',
                                          target=dl_opt_list)
        get_dl_options.start()

    def populate_tree_view(self, search_results):
        """
        Displays search results from the data api.
        Collects title, ID and duration details of each title
        """

        def populate_callback():
            count = 1
            # self.playlist_info = []
            self.clear_tree()
            for item in search_results['items']:
                self.get_title_duration(item)
                self.playlist_info.append((item['snippet']['title'],
                                           item['id']['videoId'],
                                           self.duration_call['items'][0][
                                               'contentDetails'][
                                               'duration'].encode('utf-8'),
                                           item['snippet']['description']))
                m = re.search(r'(\d+\w+)', self.playlist_info[count - 1][2])
                self.tree.insert("", '1', text=str(" "),
                                 values=(item['snippet']['title'],
                                         m.group(), item['snippet'][
                                             'description']),
                                 tags="v_")
                count += 1

        p = threading.Thread(name="Treeview", target=populate_callback)
        p.start()

    def clear_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    def get_title_duration(self, item):
        """
        Used in populate_tree_view() iteration to collect video duration based
        on the video ID
        """
        duration_call = new.yt.videos().list(part="contentDetails",
                                             id=item['id']['videoId'])
        self.duration_call = duration_call.execute()


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

    def get_user_choice(self):
        item = self.tree.focus()
        self.user_choice = self.tree.item(item, option='values')
        return self.user_choice

    def find_user_choice_in_playlist_info(self):
        for i in self.playlist_info:
            if i[0] == self.user_choice[0]:
                return i[1]


class DownloadItems(tk.Frame):
    """"""

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.dl_loc = None
        try:
#            parse = ConfigParser.SafeConfigParser()
#            config_file = open('config.ini', 'r')
            Parse.readfp(open('./config.ini'))
            self.dl_loc = Parse.get('download', 'directory')
#        except IOError:
#            logging.error('Unable to locate config file', exc_info=True)
        except Exception as e:
            print(e)

        self.choice_id = None

        self.download_dir = self.dl_loc

        self.state = tk.StringVar()
        self.opt_var = tk.StringVar()
        self.dl_options = ['none']
        self.temp_vid = None
        self.fname = None
        self.temp_vid = None
        self.video_location = None

        self.choice_dl = tk.Frame(self.parent, bg='#676767', padx=5, pady=2)
        self.choice_btns = tk.Frame(self.choice_dl, bg='#676767', padx=40,
                                    pady=10)
        self.choice_dl.grid(sticky=N+S+E+W)
        self.choice_dl.rowconfigure(0, weight=1)
        self.choice_dl.columnconfigure(0, weight=1)
        self.choice_btns.grid(row=0, column=1, rowspan=3)

        self.dl_options_lbl = tk.Label(self.choice_dl, text='Select file type',
                                       bg='#676767', fg='#f5f5f5')
        self.download_options = tk.OptionMenu(self.choice_dl, self.opt_var,
                                              *self.dl_options)
        self.download_options.config(background='#676767')
        download_label = tk.Label(self.choice_btns, text='Download',
                                  bg='#676767', fg='#f5f5f5', pady=2)
        self.download_item = ttk.Button(self.choice_btns, text="Video",
                                        command=lambda:
                                        self.download_video_callback())
        self.mp3_btn = ttk.Button(self.choice_btns, text="Mp3",
                                  command=lambda: self.get_mp3())
        self.dl_status = tk.Label(self.parent, textvariable=self.state,
                                  bd=1, relief=tk.SUNKEN, anchor=W,
                                  bg='#424242', fg='#ffffff', pady=3)
        self.choice_dl.grid_columnconfigure(0, weight=1)

        self.dl_options_lbl.grid(row=0, column=0)
        self.download_options.grid(row=1, column=0, sticky=E+W)
        download_label.grid(row=0, column=0, columnspan=2)
        self.download_item.grid(row=1, column=0, pady=2)
        self.mp3_btn.grid(row=1, column=1, pady=2)
        self.dl_status.grid(sticky=W + E + S)

    def refresh_dl_options(self):
        """Reset option variable and insert new download options"""
        self.opt_var.set('')
        self.download_options['menu'].delete(0, 'end')
        for choice in self.dl_options:
            self.download_options['menu'].add_command(label=choice,
                                                      command=tk._setit(
                                                          self.opt_var,
                                                          choice[1]))

    def get_option_choice(self):
        """Gets chosen download format"""
        dl_opt_choice = self.opt_var.get()
        for item in enumerate(self.dl_options):
            if dl_opt_choice == item[1][1]:
                return item[0]

    def check_download_video_folder(self):
        """
        Checks for separate video folder in download location. Creates
        one if none is present
        """
        try:
            if self.download_dir:
                self.video_location = self.download_dir + 'Videos/'
                logging.info(self.video_location)
            if not os.path.exists(self.video_location.encode('utf-8')):
                os.mkdir(self.video_location)
        except Exception as c:
            logging.error(c, exc_info=True)
            raise c

    def check_audio_download_folder(self):
        """
        Checks for separate audio folder in download location. Creates
        one if none is present
        """
        try:
            if self.download_dir:
                self.audio_location = self.download_dir + 'Audio/'
                self.temp_file = self.download_dir + 'temp/'

            if not os.path.exists(self.audio_location):
                os.mkdir(self.audio_location)
            if not os.path.exists(self.temp_file):
                os.mkdir(self.temp_file)
        except Exception as m:
            logging.error(m, exc_info=True)
            raise m

    def get_mp3(self):
        """Handles downloads and conversions to mp3 files"""

        self.state.set('Preparing download please wait')

        def callback():
            try:
                self.check_audio_download_folder()
                # Download mp4
                self.state.set('Downloading')
                self.temp_vid = app.result_tree.start_pafy.getbest(
                    preftype="mp4")
                self.temp_vid.download(filepath=self.temp_file,
                                  quiet=False,
                                  callback=self.progress_callback,
                                  meta=True)
                filename = self.temp_vid.filename.encode('utf-8')
                working_file = self.temp_file + filename
                encoded = self.audio_location + filename + '.mp3'
                conv = fc.convert(working_file, encoded, fc_options,
                                  timeout=None)
                self.state.set('Converting to mp3...')
                for time in conv:
                    pass

                # Delete temp file
                os.remove(working_file)
                self.state.set('Conversion complete')
            except (TypeError, AttributeError):
                tkMessageBox.showwarning('No file type', 'Select an item '
                                                      'from the results first')
                self.state.set('Download stopped')
            except OSError:
                self.missing_folder_warning()
                self.state.set('Download stopped')
            except UnicodeDecodeError:
                tkMessageBox.showerror('Error', 'Unable to process this '
                                                'video, '
                                                'please try another.')
                logging.error('unicode error', exc_info=True)
            except Exception as e:
                self.state.set('Download stopped')
                logging.error('>: ', exc_info=True)
                print('Internal error: ', e)

        temp_vid_dl = threading.Thread(name='temp_vid_dl', target=callback)
        temp_vid_dl.start()

    def progress_callback(self, total, recvd, ratio, rate, eta):
        self.update_idletasks()
        if recvd == total:

            self.state.set('Download complete')

    def download_video_callback(self):
        try:
            self.choice_id = app.result_tree.choice_id
            self.download_video(self.choice_id)
        except AttributeError:
            self.missing_id_warning()

    def download_video(self, item_id):
        self.state.set('Preparing download please wait')

        def callback():
            try:
                self.check_download_video_folder()
                stream = self.get_option_choice()
                self.p = pafy.new(item_id, size=True)
                self.video = app.result_tree.start_pafy.streams[stream]
                self.state.set("Downloading video...")
                self.video.download(filepath=self.video_location,
                                    quiet=False,
                                    callback=self.progress_callback,
                                    meta=True)
            except ValueError:
                #self.missing_id_warning()
                tkMessageBox.showwarning(title='No video ID',
                                         message='Select a video from '
                                                 'the list first')
                self.state.set('Download stopped')
            except (TypeError, AttributeError):
                tkMessageBox.showwarning('No file type', 'Select a file type '
                                                      'from the '
                                         'download options first')
                self.state.set('Download stopped')
            except OSError:
                self.missing_folder_warning()
                self.state.set('Download stopped')
            except UnicodeDecodeError:
                tkMessageBox.showerror('Error', 'Unable to process this '
                                                'video, '
                                                'please try another.')
                logging.error('unicode error', exc_info=True)
            except Exception as e:
                tkMessageBox.showerror('Error', 'There was an internal error, '
                                                'please try again.')
                self.state.set('Download stopped')
                print('Error: ', e)
                logging.error('Error: {}'.format(e), exc_info=True)



        t = threading.Thread(name='vid_download', target=callback)
        t.start()

    def missing_folder_warning(self):
        tkMessageBox.showwarning(title='Missing Download folder',
                                 message='Please choose a download '
                                         'folder in File > Settings')

    def missing_id_warning(self):
        tkMessageBox.showwarning(title='No video ID', message="Select a "
                                                              "video "
                                                              "from the "
                                                              "list first")


class MainApplication(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.parent.config(background='#676767')
        s = ttk.Style()
        s.theme_use('default')

        self.menubar = MenuBar(parent)
        self.search_items = SearchItems(parent)
        self.result_tree = ResultTree(parent)
        self.download_items = DownloadItems(parent)

        self.search_items.grid()
        self.result_tree.grid()
        self.download_items.grid()

        self.parent.update_idletasks()
        self.parent.after_idle(lambda: self.parent.minsize(
            self.parent.winfo_width(), self.parent.winfo_height()))


root = tk.Tk()
root.title('Y2M')
root.update()

app = MainApplication(root)

root.mainloop()
