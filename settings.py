import httplib2
from googleapiclient.discovery import build


class YtSettings(object):
    def __init__(self):

        self.YT_SERVICE_NAME = "youtube"
        self.YT_API_VERSION = "v3"
        self.DEVELOPER_KEY = "AIzaSyB24foHsK4r1mYHOPlAbQbUvyaWwjWQGIA"
        self.DEFAULT = 25
        self.YT_WATCH_URL = "https://www.youtube.com/watch?v="
        self.yt = build(self.YT_SERVICE_NAME, self.YT_API_VERSION,
                        http=httplib2.Http(".cache",
                                           disable_ssl_certificate_validation=True),
                        developerKey=self.DEVELOPER_KEY)

if __name__ == '__main__':
    a = YtSettings()
