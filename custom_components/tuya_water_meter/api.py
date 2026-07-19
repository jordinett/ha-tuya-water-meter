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
        self._region = region

        self._access_token: str | None = None
        self._refresh_token: str | None = None
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

    def _generate_token_signature(
        self,
        timestamp: str,
        nonce: str,
        string_to_sign: str,
    ) -> str:
        """Generate the Tuya API signature for a token request."""

        message = (
            self._client_id
            + timestamp
            + nonce
            + string_to_sign
        )

        return hmac.new(
            self._client_secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest().upper()

    async def async_get_token(self) -> dict:
        """Get an access token from Tuya Cloud."""

        path = "/v1.0/token?grant_type=1"

        timestamp = str(int(time.time() * 1000))
        nonce = uuid.uuid4().hex

        # The token request has an empty body.
        content_sha256 = hashlib.sha256(b"").hexdigest()

        # No custom headers are included in the signature.
        signed_headers = ""

        string_to_sign = (
            "GET\n"
            f"{content_sha256}\n"
            f"{signed_headers}\n"
            f"{path}"
        )

        sign = self._generate_token_signature(
            timestamp=timestamp,
            nonce=nonce,
            string_to_sign=string_to_sign,
        )

        headers = {
            "client_id": self._client_id,
            "sign": sign,
            "t": timestamp,
            "sign_method": "HMAC-SHA256",
            "nonce": nonce,
        }

        url = f"{self._base_url}{path}"

        try:
            async with self._session.get(
                url,
                headers=headers,
            ) as response:
                data = await response.json()

        except (aiohttp.ClientError, ValueError) as err:
            raise TuyaCloudApiError(
                "Unable to connect to Tuya Cloud."
            ) from err

        if not data.get("success"):
            error_message = data.get(
                "msg",
                "Unknown Tuya Cloud API error.",
            )

            raise TuyaCloudApiError(error_message)

        result = data.get("result", {})

        access_token = result.get("access_token")

        if not access_token:
            raise TuyaCloudApiError(
                "Tuya Cloud did not return an access token."
            )

        self._access_token = access_token
        self._refresh_token = result.get("refresh_token")
        self._uid = result.get("uid")

        return result

    @property
    def access_token(self) -> str | None:
        """Return the current access token."""

        return self._access_token

    @property
    def refresh_token(self) -> str | None:
        """Return the current refresh token."""

        return self._refresh_token

    @property
    def uid(self) -> str | None:
        """Return the Tuya user ID."""

        return self._uid
