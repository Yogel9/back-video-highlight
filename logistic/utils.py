from django.conf import settings


def get_public_media_url(url: str | None) -> str | None:

    if not url:
        return None

    base_url = getattr(settings, "MEDIA_PUBLIC_BASE_URL", None)
    full_url = base_url + "/video"
    if not base_url:
        return url
    for pref in ["https://minio:9000", "minio:9000", "http://minio:9000"]:
        if pref in url:
            return url.replace(pref, full_url)

    return url
