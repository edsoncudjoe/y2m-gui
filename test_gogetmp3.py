import unittest
from apiclient.discovery import build
from gogetmp3 import yt, get_videos, query, DEFAULT, YT_WATCH_URL, \
	YT_SERVICE_NAME, YT_API_VERSION, DEVELOPER_KEY, download_url


class TestGogetmp3Video(unittest.TestCase):

	@classmethod
	def setUpClass(cls):
		cls.yt = build(YT_SERVICE_NAME, YT_API_VERSION, developerKey=DEVELOPER_KEY)
		
		query="kev+brown"
		
		cls.vid_result = cls.yt.search().list(part="snippet", q=query, \
			type="video", maxResults=DEFAULT).execute()
		cls.r = get_videos(query)

	def test_length_video_list(self):
		self.assertEqual(len(self.r), DEFAULT)

	def test_get_videos_type(self):	
		self.assertNotEqual(type(self.r), type(self.vid_result))

	def test_search_url(self):
		self.assertEqual(YT_WATCH_URL, "https://www.youtube.com/watch?v=")

	def test_user_chosen_url(self):
		self.assertEqual(len(download_url), 43)



	#test watch url
	#test pafy dl
	#test pydub convert
	


if __name__ == '__main__':
	unittest.main()
