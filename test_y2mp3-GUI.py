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

        cls.yt = build(cls.YT_SERVICE_NAME, cls.YT_API_VERSION, developerKey=cls.DEVELOPER_KEY)


    def test_usr_search_output(self):
        self.usr_search = app.usr_search.get()
        print self.usr_search
        self.assertEqual(self.usr_search, 'rafiki')

    def test_optionmenu_output_is_string(self):
        self.opt_type = app.vidtype.get()
        print self.opt_type
        self.assertEqual(type(self.opt_type), type(" "))

    def test_get_usr_query(self):
        self.q = "bonobo"
        self.response = self.yt.search().list(part="snippet", q=self.q,
                                              type="video", maxResults=self.DEFAULT)
        self.assertIn(self.DEVELOPER_KEY, self.response.uri)


if __name__ == '__main__':
    unittest.main()
