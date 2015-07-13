from apiclient.discovery import build
from apiclient.errors import HttpError
#from oauth2client.tools import argparser
import logging
import pafy
from prettytable import PrettyTable
from pydub import AudioSegment

logging.basicConfig()

YT_SERVICE_NAME = "youtube"
YT_API_VERSION = "v3"
DEVELOPER_KEY = "AIzaSyAPnTeiuqIgO74mOvHe-d_pKd9526AdiI0"
DEFAULT = 25
YT_WATCH_URL = "https://www.youtube.com/watch?v="

yt = build(YT_SERVICE_NAME, YT_API_VERSION, developerKey=DEVELOPER_KEY)

#query = raw_input('enter_query: ').replace(" ", "+")
query="kev+brown"
def get_videos(query):
	"""returns list of search results from user query"""
	video_list = []
	#num = 1
	vid_response = yt.search().list(part="snippet", q=query, type="video", \
		maxResults=DEFAULT).execute()

	for item in vid_response['items']:
		video_list.append((item['id']['videoId'], item['snippet']['title']))
		#num += 1

	return video_list

def get_choice_from_results(video_list):
	"""Prints items from user results list. Returns stream url"""
	item_count = 1
	x = PrettyTable(["Video name"])
	x.align["Video name"] = "l"
	x.padding_width = 10
	for item in video_list:
		x.add_row([str(item_count) + ". " + item[1]])
		item_count += 1
	print x

	choice = int(raw_input(">:  ")) - 1

	for item in enumerate(video_list):
		if item[0] == choice:
			download_url = YT_WATCH_URL+item[1][0]

	return download_url

def dl_video(download_url):
	try:
		vid_data = pafy.new(download_url, size=True)
		vid = vid_data.getbest(preftype="mp4")
		vid.download(filepath="./temp/")
#	except HTTP Error:
#		print("This item is unavailable")
	except Exception, e:
		print(e)

#def main():
r = get_videos(query)
download_url = get_choice_from_results(r)
dl_video(download_url)
#if __name__ == '__main__':
#	main()


#song = AudioSegment.from_file('./temp/{}'.format(str(vid.filename)), format='mp4')
#song.export('./Audio/{}'.format(str(vid.filename).replace(".mp4", ".mp3")), format='mp3')

