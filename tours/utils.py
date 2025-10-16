# tours/utils.py
import hmac, hashlib, json, uuid, logging
from typing import Dict, Any, Optional
from django.conf import settings
from django.utils.timezone import now

import requests

logger = logging.getLogger(__name__)


def _client_meta(request) -> Dict[str, Any]:
    """اجمع شوية معلومات عن العميل/الطلب لإرسالها مع الـpayload."""
    ip = (
        request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
        or request.META.get("REMOTE_ADDR", "")
    )
    return {
        "ip": ip,
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "referer": request.META.get("HTTP_REFERER", ""),
        "lang": request.META.get("HTTP_ACCEPT_LANGUAGE", ""),
        "path": request.path,
        "method": request.method,
    }


def _raw_post(request) -> Dict[str, Any]:
    """
    حوّل POST لـ dict يحافظ على كل القيم (حتى لو متعددة).
    - raw: كل حقل = قائمة قيم (list)
    - raw_flat: نفس الحقول لكن لو قائمة طولها 1 نخليها قيمة مفردة
    """
    raw_pairs = list(request.POST.lists())  # [(key, [v1, v2..]), ...]
    raw = {k: v for k, v in raw_pairs}
    raw_flat = {k: (v[0] if len(v) == 1 else v) for k, v in raw.items()}
    # مهم: لا ترسل CSRF للبوابة
    raw.pop("csrfmiddlewaretoken", None)
    raw_flat.pop("csrfmiddlewaretoken", None)
    return {"raw": raw, "raw_flat": raw_flat}


def emit_booking_webhook(
    request,
    *,
    kind: str,
    source: str,
    extra: Optional[Dict[str, Any]] = None,
    schema_version: str = "1.0"
) -> None:
    """
    استدعاء Webhook موحّد إلى البوابة. لا يرفع أخطاء (Best-effort).
    - kind: "tour" | "hotel" | "general" | "transfer" | ...
    - source: وسم مصدر الإرسال (مثلاً "website:tour_detail")
    - extra: حقول إضافية (IDs، أسماء كيانات... الخ)
    """
    if not settings.PORTAL_WEBHOOK_URL or not settings.PORTAL_WEBHOOK_SECRET:
        logger.warning("Webhook not configured: URL/SECRET missing.")
        return
    if requests is None:
        logger.warning("'requests' package is not available.")
        return

    post_blob = _raw_post(request)
    payload: Dict[str, Any] = {
        "kind": kind,
        "source": source,
        "sent_at": now().isoformat(),
        "schema_version": schema_version,
        "idempotency_key": str(uuid.uuid4()),
        "client": _client_meta(request),
        **post_blob,   # يحتوي raw + raw_flat
    }

    if extra:
        # لا نطغى على raw/raw_flat
        for k, v in extra.items():
            if k in ("raw", "raw_flat"):
                continue
            payload[k] = v

    # توقيع HMAC للجسم كله
    body_bytes = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        settings.PORTAL_WEBHOOK_SECRET.encode("utf-8"),
        body_bytes,
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Portal-Signature": signature,
        "X-Idempotency-Key": payload["idempotency_key"],
    }

    try:
        requests.post(
            settings.PORTAL_WEBHOOK_URL,
            data=body_bytes,
            headers=headers,
            timeout=settings.PORTAL_WEBHOOK_TIMEOUT,
        )
    except Exception as e:
        logger.exception("Webhook call failed: %s", e)
