"""Tuya Cloud API client."""

from __future__ import annotations

import hashlib
import hmac
import time

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
        self._region = region

        self._access_token: str | None = None
        self._uid: str | None = None

        self._base_url = self._get_base_url(region)

    @staticmethod
    def _get_base_url(region: str) -> str:
        """Return the Tuya Cloud API base URL."""

        regions = {
            "cn": "https://openapi.tuyacn.com",
            "us": "https://openapi.tuyaus.com",
            "eu": "https://openapi.tuyaeu.com",
            "in": "https://openapi.tuyain.com",
        }

        return regions.get(region, regions["eu"])

    def _generate_sign(
        self,
        timestamp: str,
        string_to_sign: str,
    ) -> str:
        """Generate the Tuya API request signature."""

        message = (
            self._client_id
            + (self._access_token or "")
            + timestamp
            + string_to_sign
        )

        return hmac.new(
            self._client_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()

    async def async_get_token(self) -> dict:
        """Get an access token from Tuya Cloud."""

        timestamp = str(int(time.time() * 1000))

        sign = self._generate_sign(
            timestamp,
            "",
        )

        headers = {
            "client_id": self._client_id,
            "sign": sign,
            "t": timestamp,
            "sign_method": "HMAC-SHA256",
        }

        url = f"{self._base_url}/v1.0/token"

        async with self._session.get(
            url,
            params={"grant_type": "1"},
            headers=headers,
        ) as response:
            data = await response.json()

        if not data.get("success"):
            raise TuyaCloudApiError(
                data.get("msg", "Unknown Tuya Cloud API error")
            )

        result = data["result"]

        self._access_token = result["access_token"]
        self._uid = result.get("uid")

        return result

    @property
    def access_token(self) -> str | None:
        """Return the current access token."""

        return self._access_token

    @property
    def uid(self) -> str | None:
        """Return the Tuya user ID."""

        return self._uid
