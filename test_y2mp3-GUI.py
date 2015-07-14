import unittest
from apiclient.discovery import build
from y2mp3gui import app

class TestYT2mp3(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.YT_SERVICE_NAME = "youtube"
        cls.YT_API_VERSION = "v3"
        cls.DEVELOPER_KEY = "AIzaSyAPnTeiuqIgO74mOvHe-d_pKd9526AdiI0"
        cls.DEFAULT = 25
        cls.YT_WATCH_URL = "https://www.youtube.com/watch?v="

        cls.yt = build(cls.YT_SERVICE_NAME, cls.YT_API_VERSION,
                       developerKey=cls.DEVELOPER_KEY)

    def test_get_usr_query(self):
        self.response = self.yt.search().list(part="snippet", q=self.q,
                                              type="video", maxResults=self.DEFAULT)
        self.assertIn(self.DEVELOPER_KEY, self.response.uri)


if __name__ == '__main__':
    unittest.main()
