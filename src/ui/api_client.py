import httpx


class ApiError(Exception): ...


class ApiClient:
    """La interfaz habla con el backend solo por HTTP (Frontend -> API -> BD)."""

    def __init__(self, base: str = "http://127.0.0.1:8000"):
        self.base = base

    def _request(self, method: str, path: str, **kwargs):
        try:
            r = httpx.request(method, self.base + path, timeout=10.0, **kwargs)
        except httpx.HTTPError as exc:
            raise ApiError(f"Sin conexión con la API: {exc}") from exc
        if r.status_code >= 400:
            try:
                detail = r.json().get("detail", r.text)
            except Exception:
                detail = r.text
            raise ApiError(str(detail))
        return r.json() if r.content else None

    def get(self, path, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, json=None):
        return self._request("POST", path, json=json)

    def put(self, path, json=None):
        return self._request("PUT", path, json=json)
    