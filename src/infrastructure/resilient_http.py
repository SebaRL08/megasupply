import time
import httpx

class ExternalAPIError(Exception): ...
class CircuitOpenError(Exception): ...

class CircuitBreaker:
    """CLOSED -> OPEN tras N fallos; OPEN -> HALF_OPEN tras el tiempo de recuperación."""
    def __init__(self, failure_threshold=3, recovery_timeout=30.0):
        self.threshold, self.recovery = failure_threshold, recovery_timeout
        self.state, self.failures, self.opened_at = "CLOSED", 0, 0.0

    def before_call(self):
        if self.state == "OPEN":
            if time.monotonic() - self.opened_at >= self.recovery:
                self.state = "HALF_OPEN"
            else:
                raise CircuitOpenError("Circuit is OPEN: external API temporarily blocked")

    def on_success(self):
        self.failures, self.state = 0, "CLOSED"

    def on_failure(self):
        self.failures += 1
        if self.state == "HALF_OPEN" or self.failures >= self.threshold:
            self.state, self.opened_at = "OPEN", time.monotonic()

class ResilientClient:
    def __init__(self, timeout=5.0, retries=3, base_delay=0.5, breaker=None):
        self.timeout, self.retries, self.base_delay = timeout, retries, base_delay
        self.breaker = breaker or CircuitBreaker()

    def get_json(self, url, params=None):
        self.breaker.before_call()
        last = None
        for attempt in range(self.retries):
            try:
                r = httpx.get(url, params=params, timeout=self.timeout)
                r.raise_for_status()
                self.breaker.on_success()
                return r.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code < 500:  # error del cliente: no se reintenta
                    raise ExternalAPIError(f"HTTP {e.response.status_code}") from e
                last = e
            except (httpx.TimeoutException, httpx.TransportError) as e:
                last = e
            if attempt < self.retries - 1:
                time.sleep(self.base_delay * 2 ** attempt)  # backoff exponencial: 0.5s, 1s...
        self.breaker.on_failure()
        raise ExternalAPIError(f"External API failed after {self.retries} attempts") from last
    