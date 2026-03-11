from __future__ import annotations

import random
import time

from app.drivers.base import ComputeDriver


class MockOpenStackDriver(ComputeDriver):
    """
    A tiny stand-in for OpenStack compute actions.

    The API is synchronous for simplicity, but we simulate small delays to mimic real calls.
    """

    def __init__(self, *, error_rate: float = 0.0, min_delay_ms: int = 10, max_delay_ms: int = 50) -> None:
        self._error_rate = max(0.0, min(1.0, error_rate))
        self._min_delay_ms = min_delay_ms
        self._max_delay_ms = max_delay_ms

    def _maybe_fail(self) -> None:
        if self._error_rate > 0 and random.random() < self._error_rate:
            raise RuntimeError("mock driver failure")

    def _delay(self) -> None:
        if self._max_delay_ms <= 0:
            return
        time.sleep(random.randint(self._min_delay_ms, self._max_delay_ms) / 1000.0)

    def provision(self, vm_id: str) -> None:
        self._delay()
        self._maybe_fail()

    def start(self, vm_id: str) -> None:
        self._delay()
        self._maybe_fail()

    def stop(self, vm_id: str) -> None:
        self._delay()
        self._maybe_fail()

    def reboot(self, vm_id: str, hard: bool) -> None:
        self._delay()
        self._maybe_fail()

    def resize(self, vm_id: str, new_flavor: str) -> None:
        self._delay()
        self._maybe_fail()

    def delete(self, vm_id: str) -> None:
        self._delay()
        self._maybe_fail()
