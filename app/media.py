import base64
import io
import logging
import os
from datetime import UTC, datetime, timedelta
from urllib.request import urlopen
from urllib.parse import urlparse, urlunparse
from uuid import uuid4

from minio import Minio
from openai import OpenAI

logger = logging.getLogger(__name__)


def _get_minio_client() -> tuple[Minio, str, bool] | tuple[None, str, bool]:
    endpoint = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    bucket = os.getenv("MINIO_BUCKET", "echodiary")
    secure = os.getenv("MINIO_SECURE", "false").lower() == "true"

    if not endpoint or not access_key or not secret_key:
        return None, bucket, secure

    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
    return client, bucket, secure


def generate_diary_image_png_bytes(*, diary_text: str) -> bytes | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or os.getenv("ECHODIARY_DISABLE_LLM") == "true":
        return None

    client = OpenAI(api_key=api_key)
    try:
        response = client.images.generate(
            model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"),
            prompt=(
                "다음 한국어 일기 내용을 기반으로, 따뜻하고 일상적인 분위기의 장면 1개를 묘사한 이미지 생성:\n"
                f"{diary_text}\n"
                "요구: 인물 식별이 가능한 실존 인물 스타일 금지, 안전하고 일반적인 일상 장면, 텍스트 오버레이 없음"
            ),
            # 2026-02 기준 OpenAI Images API 지원값: 1024x1024 | 1024x1536 | 1536x1024 | auto
            size=os.getenv("OPENAI_IMAGE_SIZE", "1024x1024"),
        )
        if not response.data:
            return None

        first = response.data[0]
        encoded = getattr(first, "b64_json", None)
        if encoded:
            return base64.b64decode(encoded)

        image_url = getattr(first, "url", None)
        if image_url:
            with urlopen(image_url, timeout=20) as res:
                return res.read()

        return None
    except Exception as exc:  # noqa: BLE001
        logger.warning("Image generation failed: %s", exc)
        return None


def upload_image_to_minio(*, image_bytes: bytes, account_id: str) -> str | None:
    client, bucket, _secure = _get_minio_client()
    if client is None:
        return None

    found = client.bucket_exists(bucket)
    if not found:
        client.make_bucket(bucket)

    date_prefix = datetime.now(UTC).strftime("%Y/%m/%d")
    object_name = f"diary-images/{account_id}/{date_prefix}/{uuid4()}.png"
    client.put_object(
        bucket,
        object_name,
        data=io.BytesIO(image_bytes),
        length=len(image_bytes),
        content_type="image/png",
    )

    # Store object path only. URL is issued per-request as presigned URL.
    return object_name


def _normalize_object_name(image_ref: str, bucket: str) -> str:
    if image_ref.startswith("http://") or image_ref.startswith("https://"):
        parsed = urlparse(image_ref)
        path = parsed.path.lstrip("/")
        prefix = f"{bucket}/"
        return path[len(prefix):] if path.startswith(prefix) else path
    return image_ref


def _apply_public_base_url(url: str) -> str:
    public_base = os.getenv("MINIO_PUBLIC_BASE_URL", "").strip()
    if not public_base:
        return url

    parsed_url = urlparse(url)
    parsed_base = urlparse(public_base)
    if not parsed_base.scheme or not parsed_base.netloc:
        return url

    return urlunparse(
        (
            parsed_base.scheme,
            parsed_base.netloc,
            parsed_url.path,
            parsed_url.params,
            parsed_url.query,
            parsed_url.fragment,
        )
    )


def create_presigned_image_url(*, image_ref: str, expires_seconds: int = 300) -> str | None:
    client, bucket, _secure = _get_minio_client()
    if client is None or not image_ref:
        return None

    object_name = _normalize_object_name(image_ref, bucket)
    try:
        signed = client.presigned_get_object(bucket, object_name, expires=timedelta(seconds=expires_seconds))
        return _apply_public_base_url(signed)
    except Exception:  # noqa: BLE001
        return None


def get_image_from_minio(*, image_ref: str) -> tuple[bytes, str] | tuple[None, None]:
    client, bucket, _secure = _get_minio_client()
    if client is None or not image_ref:
        return None, None

    object_name = _normalize_object_name(image_ref, bucket)
    response = None
    try:
        response = client.get_object(bucket, object_name)
        content_type = response.headers.get("Content-Type", "application/octet-stream")
        data = response.read()
        return data, content_type
    except Exception:  # noqa: BLE001
        return None, None
    finally:
        if response is not None:
            response.close()
            response.release_conn()
