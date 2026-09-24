"""Bounded imports of reviewed thumbnails into the project's R2 bucket."""

import hashlib
import http.client
import io
import ipaddress
import socket
import ssl
import time
import warnings
from datetime import timedelta
from urllib.parse import urljoin, urlsplit

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from PIL import Image, ImageOps, UnidentifiedImageError

from .models import Project, validate_thumbnail_url

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 16_000_000


class ThumbnailImportError(Exception):
    """A content-free error code safe to retain in the admin."""


def public_addresses(host):
    """Reject the entire DNS result if any answer is not a global address."""
    answers = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    addresses = list(dict.fromkeys(answer[4][0] for answer in answers))

    def allowed(ip):
        address = ipaddress.ip_address(ip)
        if address.version == 6 and address.ipv4_mapped:
            address = address.ipv4_mapped
        if not address.is_global or address.is_multicast or address.is_reserved:
            return False
        if address.version == 6:
            return not (
                address.sixtofour
                or address.teredo
                or address in ipaddress.ip_network("64:ff9b::/96")
            )
        return True

    if not addresses or not all(allowed(ip) for ip in addresses):
        raise ThumbnailImportError("private_address")
    return addresses


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    """Connect to the validated IP without resolving the hostname a second time."""

    def __init__(self, host, address, timeout):
        super().__init__(host, port=443, timeout=timeout, context=ssl.create_default_context())
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


def fetch_image(url):
    """HTTPS only, pinned DNS at every redirect, no cookies/proxies/auth headers."""
    deadline = time.monotonic() + 20
    for _ in range(4):
        validate_thumbnail_url(url)
        parsed = urlsplit(url)
        if parsed.port not in (None, 443):
            raise ThumbnailImportError("invalid_port")
        addresses = public_addresses(parsed.hostname)
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ThumbnailImportError("download_timeout")
        connection = PinnedHTTPSConnection(parsed.hostname, addresses[0], min(5, remaining))
        try:
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            connection.request(
                "GET",
                path,
                headers={
                    "User-Agent": "BuiltWithBend-thumbnail/1.0",
                    "Accept": "image/png,image/jpeg,image/webp,image/gif",
                    "Accept-Encoding": "identity",
                },
            )
            response = connection.getresponse()
            if response.status in (301, 302, 303, 307, 308):
                location = response.getheader("Location")
                if not location:
                    raise ThumbnailImportError("invalid_redirect")
                url = urljoin(url, location)
                continue
            if response.status != 200:
                raise ThumbnailImportError("source_unavailable")
            return read_image_body(response, connection, deadline)
        finally:
            connection.close()
    raise ThumbnailImportError("too_many_redirects")


def read_image_body(response, connection, deadline):
    size = response.getheader("Content-Length")
    if size and (not size.isdecimal() or int(size) > MAX_BYTES):
        raise ThumbnailImportError("image_too_large")
    if response.getheader("Content-Encoding", "identity").lower() != "identity":
        raise ThumbnailImportError("unsupported_encoding")
    body = bytearray()
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ThumbnailImportError("download_timeout")
        if connection.sock is not None:
            connection.sock.settimeout(min(5, remaining))
        chunk = response.read1(min(64 * 1024, MAX_BYTES + 1 - len(body)))
        if not chunk:
            return bytes(body)
        body.extend(chunk)
        if len(body) > MAX_BYTES:
            raise ThumbnailImportError("image_too_large")


def normalize_image(data):
    """Decode raster content, strip metadata, and store a bounded static WebP."""
    if len(data) > MAX_BYTES:
        raise ThumbnailImportError("image_too_large")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as original:
                if original.format not in ("PNG", "JPEG", "WEBP", "GIF"):
                    raise ThumbnailImportError("unsupported_image")
                if original.width * original.height > MAX_PIXELS:
                    raise ThumbnailImportError("too_many_pixels")
                original.seek(0)
                image = ImageOps.exif_transpose(original).convert("RGBA")
                image.thumbnail((1600, 1200))
                # Start with a fresh image so EXIF/ICC/comments cannot be carried forward.
                clean = Image.new("RGBA", image.size)
                clean.paste(image)
                output = io.BytesIO()
                clean.save(output, format="WEBP", quality=85, method=4)
                encoded = output.getvalue()
                if len(encoded) > MAX_BYTES:
                    raise ThumbnailImportError("image_too_large")
                return encoded
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombWarning,
        Image.DecompressionBombError,
    ) as exc:
        raise ThumbnailImportError("invalid_image") from exc


def r2_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.THUMBNAIL_R2_ENDPOINT_URL,
        aws_access_key_id=settings.THUMBNAIL_R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.THUMBNAIL_R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(
            signature_version="s3v4",
            connect_timeout=5,
            read_timeout=10,
            retries={"max_attempts": 2},
            s3={"addressing_style": "path"},
        ),
    )


def import_project_thumbnail(project_id):
    if not settings.THUMBNAIL_R2_ENABLED:
        return "disabled"
    project = Project.objects.filter(pk=project_id, status=Project.Status.PUBLISHED).first()
    if not project or not project.thumbnail_url:
        return "skipped"
    source = project.thumbnail_url
    if project.thumbnail_key and project.thumbnail_imported_source == source:
        return "unchanged"
    try:
        encoded = normalize_image(fetch_image(source))
        key = f"projects/{project.pk}/{hashlib.sha256(encoded).hexdigest()}.webp"
        # Recheck after the download; never publish an image for an edited/unpublished record.
        with transaction.atomic():
            current = Project.objects.select_for_update().get(pk=project.pk)
            if current.thumbnail_url != source or current.status != Project.Status.PUBLISHED:
                return "stale"
            client = r2_client()
            try:
                client.put_object(
                    Bucket=settings.THUMBNAIL_R2_BUCKET,
                    Key=key,
                    Body=encoded,
                    ContentType="image/webp",
                    CacheControl="public, max-age=31536000, immutable",
                )
            finally:
                client.close()
            Project.objects.filter(pk=project.pk).update(
                thumbnail_key=key,
                thumbnail_imported_source=source,
                thumbnail_attempted_at=timezone.now(),
                thumbnail_error="",
            )
        return "ready"
    except Project.DoesNotExist:
        return "stale"
    except ThumbnailImportError as exc:
        error = str(exc)
    except (ValidationError, ValueError, UnicodeError):
        error = "invalid_source"
    except (OSError, http.client.HTTPException):
        error = "source_unavailable"
    except (BotoCoreError, ClientError):
        error = "storage_unavailable"
    Project.objects.filter(pk=project.pk, thumbnail_url=source).update(
        thumbnail_attempted_at=timezone.now(),
        thumbnail_error=error,
    )
    return "failed"


def refresh_thumbnails(limit=5):
    """Reconcile approved records every minute; retry failures after fifteen minutes."""
    result = {"ready": 0, "failed": 0, "skipped": 0}
    if not settings.THUMBNAIL_R2_ENABLED:
        return {**result, "disabled": True}
    if not cache.add("directory:r2-thumbnails", True, timeout=600):
        return {**result, "locked": True}
    try:
        cutoff = timezone.now() - timedelta(minutes=15)
        candidates = (
            Project.objects.filter(status=Project.Status.PUBLISHED)
            .exclude(thumbnail_url="")
            .filter(Q(thumbnail_key="") | ~Q(thumbnail_imported_source=F("thumbnail_url")))
            .filter(Q(thumbnail_error="") | Q(thumbnail_attempted_at__lt=cutoff))
            .order_by(F("thumbnail_attempted_at").asc(nulls_first=True), "pk")
            .values_list("pk", flat=True)[: min(max(limit, 1), 5)]
        )
        for pk in candidates:
            outcome = import_project_thumbnail(pk)
            result[outcome if outcome in result else "skipped"] += 1
        return result
    finally:
        cache.delete("directory:r2-thumbnails")
