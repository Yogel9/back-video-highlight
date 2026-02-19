import logging
import os
import tempfile
from urllib.parse import urlparse

import requests
import yt_dlp

logger = logging.getLogger(__name__)

DIRECT_VIDEO_EXTENSIONS = (".mp4", ".webm", ".mkv", ".mov", ".avi", ".m4v")
YOUTUBE_DOMAINS = ("youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com")


class ResourceNotFoundError(Exception):
    """Ресурс (видео) не найден или недоступен."""


class NotAVideoError(Exception):
    """Предоставлена ссылка не на видео."""


class VideoUploader:
    ydl_opts = {
        'format': 'bestvideo[height<=1080]',
        'outtmpl': '%(title)s_%(height)s.%(ext)s',
        "merge_output_format": "mp4",
        'restrictfilenames': True,
        'nooverwrites': True,
        'quiet': False,
    }

    def __init__(self, url, low_resolution=False):
        self.url = url
        self.video_file = None
        self.low_resolution = low_resolution
        self._temp_dir = tempfile.mkdtemp()

    def _is_youtube_url(self, url):
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return any(d in domain for d in YOUTUBE_DOMAINS)

    def _is_direct_video_url(self, url):
        parsed = urlparse(url)
        path = parsed.path.lower()
        return path.endswith(DIRECT_VIDEO_EXTENSIONS)

    def validate_url(self):
        if self._is_youtube_url(self.url):
            try:
                opts = {"quiet": True, "no_warnings": True, "extract_flat": False}
                with yt_dlp.YoutubeDL(opts) as ydl:
                    info = ydl.extract_info(self.url, download=False)
                    if info is None:
                        raise ResourceNotFoundError("Видео недоступно для загрузки")
            except yt_dlp.utils.DownloadError as e:
                logger.warning("YouTube: ресурс недоступен %s: %s", self.url, e)
                raise ResourceNotFoundError("Ресурс не найден или недоступен") from e
        elif self._is_direct_video_url(self.url):
            try:
                response = requests.head(self.url, timeout=15, allow_redirects=True)
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                if content_type and not any(
                    ct in content_type for ct in ("video/", "application/octet-stream")
                ):
                    raise NotAVideoError("Предоставлена ссылка не на видео")
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    raise ResourceNotFoundError("Ресурс не найден") from e
                raise ResourceNotFoundError("Не удалось загрузить видео") from e
        else:
            raise NotAVideoError(
                f"Предоставлена ссылка не на видео. ",
                f"Поддерживаются YouTube и прямые ссылки на видео ({DIRECT_VIDEO_EXTENSIONS})"
            )

    def _download_from_youtube(self):
        try:
            opts = {
                **self.ydl_opts,
                "outtmpl": os.path.join(self._temp_dir, "%(id)s.%(ext)s"),
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=True)

                if info is None:
                    raise ResourceNotFoundError("Видео недоступно для загрузки")

                self.video_file = ydl.prepare_filename(info)

                if not os.path.exists(self.video_file):
                    files = [
                        f for f in os.listdir(self._temp_dir)
                        if f.endswith((".mp4", ".webm", ".mkv", ".m4a"))
                    ]

                    if not files:
                        raise ResourceNotFoundError("Не удалось загрузить видео")

                    self.video_file = os.path.join(self._temp_dir, files[0])

            return self.video_file
        except yt_dlp.utils.DownloadError as e:
            logger.warning("YouTube: ресурс недоступен %s: %s", self.url, e)
            raise ResourceNotFoundError("Ресурс не найден или недоступен") from e
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.exception("Ошибка загрузки YouTube %s: %s", self.url, e)
            raise ResourceNotFoundError("Не удалось загрузить видео") from e

    def _download_direct(self):
        try:
            parsed = urlparse(self.url)
            filename = os.path.basename(parsed.path) or "video.mp4"
            filepath = os.path.join(self._temp_dir, filename)
            response = requests.get(self.url, stream=True, timeout=60)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()
            if content_type and not any(
                ct in content_type for ct in ("video/", "application/octet-stream")
            ):
                raise NotAVideoError("Предоставлена ссылка не на видео")
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.video_file = filepath
            return self.video_file
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise ResourceNotFoundError("Ресурс не найден") from e
            logger.exception("Ошибка загрузки по прямой ссылке %s: %s", self.url, e)
            raise ResourceNotFoundError("Не удалось загрузить видео") from e
        except NotAVideoError:
            raise
        except Exception as e:
            logger.exception("Ошибка загрузки по прямой ссылке %s: %s", self.url, e)
            raise ResourceNotFoundError("Не удалось загрузить видео") from e

    def upload(self):
        if self._is_youtube_url(self.url):
            return self._download_from_youtube()
        if self._is_direct_video_url(self.url):
            return self._download_direct()
        raise NotAVideoError("Предоставлена ссылка не на видео. "
                             "Поддерживаются YouTube и прямые ссылки "
                             "на видео (.mp4, .webm и т.д.)")

    def cleanup(self):
        if self._temp_dir and os.path.isdir(self._temp_dir):
            try:
                for f in os.listdir(self._temp_dir):
                    os.remove(os.path.join(self._temp_dir, f))
                os.rmdir(self._temp_dir)
            except OSError as e:
                logger.warning("Не удалось удалить temp-директорию: %s", e)