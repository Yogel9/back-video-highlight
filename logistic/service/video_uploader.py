from pytubefix import YouTube
from pytubefix.exceptions import MaxRetriesExceeded

class VideoUploader:

    def __init__(self, url):
        self.url = url
        self.video_file = None

    def upload(self):
        try:
            yt = YouTube(self.url)
            self.video_file = yt.streams.get_highest_resolution().download()
        except MaxRetriesExceeded:
            self.video_file = None
        return self.video_file