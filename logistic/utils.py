from django.conf import settings


def get_public_media_url(url: str | None) -> str | None:

    if not url:
        return None

    base_url = getattr(settings, "MEDIA_PUBLIC_BASE_URL", None)

    if not base_url:
        return url

    if "minio" in url:
        return url.replace("minio", base_url)

    return url
