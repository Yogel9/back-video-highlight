from pytubefix import YouTube
from pytubefix.exceptions import MaxRetriesExceeded

class VideoUploader:

    def __init__(self, url, low_resolution=False):
        self.url = url
        self.video_file = None
        self.low_resolution = low_resolution

    def upload(self):
        try:
            yt = YouTube(self.url)
            streams = yt.streams
            stream = streams.get_lowest_resolution() if self.low_resolution else streams.get_highest_resolution()
            self.video_file = stream.download()
        except MaxRetriesExceeded:
            self.video_file = None
        return self.video_file