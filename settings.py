from apiclient.discovery import build


class YtSettings(object):
    def __init__(self):
        self.self = self

        self.YT_SERVICE_NAME = "youtube"
        self.YT_API_VERSION = "v3"
        self.DEVELOPER_KEY = "AIzaSyB24foHsK4r1mYHOPlAbQbUvyaWwjWQGIA"
        self.DEFAULT = 25
        self.YT_WATCH_URL = "https://www.youtube.com/watch?v="
        try:
            self.yt = build(self.YT_SERVICE_NAME, self.YT_API_VERSION,
                            developerKey=self.DEVELOPER_KEY)
        except Exception as e:
            print("GoogleError: {}".format(e))


if __name__ == '__main__':
    a = YtSettings()
