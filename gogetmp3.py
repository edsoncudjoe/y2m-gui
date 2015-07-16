from apiclient.discovery import build
from apiclient.errors import HttpError
# from oauth2client.tools import argparser
import logging
import os
import pafy
from prettytable import PrettyTable
from pydub import AudioSegment

logging.basicConfig()

class YtData(object):

    def __init__(self):
        self.self = self

        self.YT_SERVICE_NAME = "youtube"
        self.YT_API_VERSION = "v3"
        self.DEVELOPER_KEY = "AIzaSyAPnTeiuqIgO74mOvHe-d_pKd9526AdiI0"
        self.DEFAULT = 25
        self.YT_WATCH_URL = "https://www.youtube.com/watch?v="

        self.yt = build(self.YT_SERVICE_NAME, self.YT_API_VERSION,
                    developerKey=self.DEVELOPER_KEY)

        # self.query = raw_input('enter_query: ').replace(" ", "+")
        self.query = ""#raw_input("Search: ")
        self.vtype = ""#raw_input("Enter video or playlist")


    def get_videos(self, query, vtype):
        """returns list of search results from user query"""
        self.video_list = []
        self.pl_ids = []
        # num = 1
        self.vid_response = self.yt.search().list(part="snippet", q=query,
                                                  type=vtype, maxResults=self.
                                                  DEFAULT).execute()
        if vtype == "video":
            for item in self.vid_response['items']:
                self.video_list.append((item['id']['videoId'],
                                        item['snippet']['title']))
        elif vtype == "playlist":
            for item in self.vid_response['items']:
                self.video_list.append((item['id']['playlistId'],
                                        item['snippet']['title'],))
            for v in self.video_list:
                self.ic = self.yt.playlists().list(part="contentDetails",
                                              id=v[0]).execute()
                for i in self.ic['items']:
                    self.pl_ids.append((v[0], v[1], i["contentDetails"][
                        "itemCount"]))
        else:
            print("None found")
        # num += 1

        return self.video_list


    def get_choice_from_results(self, video_list, vtype):
        """Prints items from user results list. Returns stream url"""
        self.item_count = 1

        if vtype == "video":
            self.x = PrettyTable(["Video name"])
            self.x.align["Video name"] = "l"
            self.x.padding_width = 10
            for item in self.video_list:
                self.x.add_row([str(self.item_count) + ". " + item[1]])
                self.item_count += 1
            print self.x
        elif vtype == "playlist":
            self.x = PrettyTable(["Playlist", "Items"])
            self.x.align["Video name"] = "l"
            self.x.padding_width = 10
            for item in self.pl_ids:
                self.x.add_row([str(self.item_count) + ". " + item[1],
                                str(item[2]) + " videos"])
                self.item_count += 1
            print self.x

        self.choice = int(raw_input(">:  ")) - 1

        for item in enumerate(self.video_list):
            if item[0] == self.choice:
                self.download_url = self.YT_WATCH_URL + item[1][0]

        return self.download_url


    def dl_video(self, download_url):
        try:
            self.vid_data = pafy.new(download_url, size=True)
            self.vid = self.vid_data.getbest(preftype="mp4")
            self.vid.download(filepath="./Video/")
            print("video extraction complete!")
        except Exception, e:
            print(e)


    def dl_mp3(self, download_url):
        try:
            self.vid_data = pafy.new(download_url, size=True)
            self.vid = self.vid_data.getbest(preftype="mp4")
            self.fname = str(self.vid.filename)
            self.vid.download(filepath="./temp/")

            self.song = AudioSegment.from_file('./temp/{}'.format(str(
                self.vid.filename)), format='mp4')
            self.song.export('./Audio/{}'.format(self.fname).replace(".mp4",
                                                                 ".mp3"),
                             format='mp3')
            os.remove("./temp/{}".format(self.fname))
            print("mp3 extraction complete!")
        except Exception, e:
            print(e)


def main():
    n = YtData()
    r = n.get_videos(n.query, n.vtype)
    download_url = n.get_choice_from_results(r, n.vtype)

    dl_item = raw_input("vid or mp3: ")
    if dl_item == "vid":
        n.dl_video(download_url)
    elif dl_item == "mp3":
        n.dl_mp3(download_url)
if __name__ == '__main__':
    main()



