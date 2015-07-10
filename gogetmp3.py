from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import logging
import pafy
from prettytable import PrettyTable


logging.basicConfig()

YT_SERVICE_NAME = "youtube"
YT_API_VERSION = "v3"
DEVELOPER_KEY = "AIzaSyAPnTeiuqIgO74mOvHe-d_pKd9526AdiI0"
DEFAULT = 25
YT_WATCH_URL = "https://www.youtube.com/watch?v="

# HTTP_REQUEST = "https://www.googleapis.com/youtube/v3/search"




yt = build(YT_SERVICE_NAME, YT_API_VERSION, developerKey=DEVELOPER_KEY)

#query = raw_input('enter_query: ').replace(" ", "+")
query="kev+brown"
def get_videos(query):
	"""returns list of search results"""
	video_list = []
	#num = 1
	vid_response = yt.search().list(part="snippet", q=query, type="video", \
		maxResults=DEFAULT).execute()

	for item in vid_response['items']:
		video_list.append((item['id']['videoId'], item['snippet']['title']))
		#num += 1

	return video_list


r = get_videos(query)

item_count = 0
x = PrettyTable(["Video name"])
x.align["Video name"] = "l"
x.padding_width = 10
for item in r:
    x.add_row([str(item_count) + ". " + item[1]])
    item_count += 1
print x

choice = int(raw_input(">:  "))

for item in enumerate(r):
	if item[0] == choice:
		print YT_WATCH_URL+item[1][0] #send this link to pafy and pydub

		#test outcome


