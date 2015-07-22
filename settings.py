from apiclient.discovery import build
from apiclient.errors import HttpError


class YtSettings(object):
    def __init__(self):
        self.self = self

        self.YT_SERVICE_NAME = "youtube"
        self.YT_API_VERSION = "v3"
        self.DEVELOPER_KEY = "AIzaSyA6NftYUAeddmV_cBB5NmfCE0C5EKTZbbc"
        self.DEFAULT = 25
        self.YT_WATCH_URL = "https://www.youtube.com/watch?v="

        self.yt = build(self.YT_SERVICE_NAME, self.YT_API_VERSION,
                        developerKey=self.DEVELOPER_KEY)


if __name__ == '__main__':
    a = YtSettings()
