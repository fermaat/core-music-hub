"""HTTP client used by downstream apps (e.g. fante)."""

from typing import Any

import httpx


class SongNotFoundError(LookupError):
    """Raised by the client when /play or /next returns 404."""


class MusicHubClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8600",
        timeout: int = 30,
        _client: httpx.Client | None = None,
    ) -> None:
        self._base = base_url.rstrip("/")
        self._timeout = timeout
        self._client = _client

    def _get(self, path: str) -> httpx.Response:
        if self._client is not None:
            return self._client.get(f"{self._base}{path}", timeout=self._timeout)
        return httpx.get(f"{self._base}{path}", timeout=self._timeout)

    def _post(self, path: str, **kwargs: Any) -> httpx.Response:
        if self._client is not None:
            return self._client.post(f"{self._base}{path}", timeout=self._timeout, **kwargs)
        return httpx.post(f"{self._base}{path}", timeout=self._timeout, **kwargs)

    def health(self) -> bool:
        response = self._get("/health")
        response.raise_for_status()
        return bool(response.json().get("status") == "ok")

    def catalog(self) -> list[dict[str, Any]]:
        response = self._get("/catalog")
        response.raise_for_status()
        return response.json().get("songs", [])  # type: ignore[no-any-return]

    def play(
        self,
        *,
        alias: str | None = None,
        id: str | None = None,
        mood: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        body = {"alias": alias, "id": id, "mood": mood, "tags": tags}
        body = {k: v for k, v in body.items() if v is not None}
        response = self._post("/play", json=body)
        if response.status_code == 404:
            raise SongNotFoundError(response.json().get("detail", ""))
        response.raise_for_status()
        return response.json()["playing"]  # type: ignore[no-any-return]

    def stop(self) -> None:
        response = self._post("/stop")
        response.raise_for_status()

    def next(self) -> dict[str, Any]:
        response = self._post("/next")
        if response.status_code == 404:
            raise SongNotFoundError("No other songs available")
        response.raise_for_status()
        return response.json()["playing"]  # type: ignore[no-any-return]

    def status(self) -> dict[str, Any]:
        response = self._get("/status")
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
