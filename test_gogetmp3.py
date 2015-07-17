import unittest
from apiclient.discovery import build
from gogetmp3 import YtData


class TestGogetmp3Video(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.n = YtData()

    def test_dl_mp3(self):
	    self.assertEqual(self.n.song.endswith(), '.ogg')

    # test watch url
    # test pafy dl
    # test pydub convert


if __name__ == '__main__':
    unittest.main()
