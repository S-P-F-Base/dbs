import logging
from enum import IntEnum
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger(__name__)

OVERLORD_SOCKET = Path("/run/spf/overlord.sock")


class AccessBitFlags(IntEnum):
    READ = 1 << 0
    CREATE = 1 << 1
    UPDATE = 1 << 2
    DELETE = 1 << 3


BASE_ACCESS: dict[str, Any] = {
    "all_access": False,
    "manage_access": False,
    "svr": {
        "user": 0,
    },
}

BASE_OPTIN: dict[str, bool] = {
    "": False,
}


class Constants:
    _data: dict[str, str] = {}

    @classmethod
    async def req_from_over(cls) -> None:
        transport = httpx.AsyncHTTPTransport(uds=str(OVERLORD_SOCKET))

        try:
            async with httpx.AsyncClient(
                transport=transport,
                timeout=5.0,
            ) as client:
                resp = await client.get("http://overlord/config")

            if resp.status_code != 200:
                log.warning(
                    "Overlord returned %s for %s",
                    resp.status_code,
                    "http://overlord/config",
                )
                cls._data = {}

            cls._data = resp.json()

        except httpx.ConnectError:
            log.warning("Overlord socket not available: %s", OVERLORD_SOCKET)
            cls._data = {}

        except httpx.TimeoutException:
            log.warning("Overlord request timeout: %s", "http://overlord/config")
            cls._data = {}

        except Exception as exc:
            log.exception(
                "Unexpected error while fetching %s: %s",
                "http://overlord/config",
                exc,
            )
            cls._data = {}

    @classmethod
    def get_all_const(cls) -> dict[str, str]:
        return cls._data
