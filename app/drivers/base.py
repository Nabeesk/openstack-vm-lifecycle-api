from __future__ import annotations

from abc import ABC, abstractmethod


class ComputeDriver(ABC):
    @abstractmethod
    def provision(self, vm_id: str) -> None: ...

    @abstractmethod
    def start(self, vm_id: str) -> None: ...

    @abstractmethod
    def stop(self, vm_id: str) -> None: ...

    @abstractmethod
    def reboot(self, vm_id: str, hard: bool) -> None: ...

    @abstractmethod
    def resize(self, vm_id: str, new_flavor: str) -> None: ...

    @abstractmethod
    def delete(self, vm_id: str) -> None: ...
