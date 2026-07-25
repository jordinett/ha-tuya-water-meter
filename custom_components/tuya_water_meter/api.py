"""Tuya Cloud API client."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid
import aiohttp

class TuyaCloudApiError(Exception):
    """Exception raised when the Tuya Cloud API returns an error."""

class TuyaCloudApi:
    """Client for the Tuya Cloud API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_id: str,
        client_secret: str,
        region: str = "eu",
    ) -> None:
        """Initialize the Tuya Cloud API client."""
        self._session = session
        self._client_id = client_id
        self._client_secret = client_secret
        self._access_token: str | None = None
        self._base_url = self._get_base_url(region)

    @staticmethod
    def _get_base_url(region: str) -> str:
        regions = {
            "cn": "https://openapi.tuyacn.com",
            "us": "https://openapi.tuyaus.com",
            "eu": "https://openapi.tuyaeu.com",
            "in": "https://openapi.tuyain.com",
        }
        return regions.get(region, regions["eu"])

    def _generate_token_signature(self, timestamp: str, nonce: str, string_to_sign: str) -> str:
        message = self._client_id + timestamp + nonce + string_to_sign
        return hmac.new(self._client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest().upper()

    def _generate_api_signature(self, timestamp: str, nonce: str, string_to_sign: str) -> str:
        message = self._client_id + self._access_token + timestamp + nonce + string_to_sign
        return hmac.new(self._client_secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest().upper()

    async def async_get_token(self) -> str:
        """Get or refresh an access token from Tuya Cloud."""
        path = "/v1.0/token?grant_type=1"
        timestamp = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex
        content_sha256 = hashlib.sha256(b"").hexdigest()

        string_to_sign = f"GET\n{content_sha256}\n\n{path}"
        sign = self._generate_token_signature(timestamp, nonce, string_to_sign)

        headers = {
            "client_id": self._client_id,
            "sign": sign,
            "t": timestamp,
            "sign_method": "HMAC-SHA256",
            "nonce": nonce,
        }
