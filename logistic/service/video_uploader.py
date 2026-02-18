from pytubefix import YouTube

class VideoUploader:

    def __init__(self, url):
        self.url = url

    def upload(self):
        yt = YouTube(self.url)
        self.video_file = yt.streams.get_highest_resolution().download()
        return self.file