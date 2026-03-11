from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from threading import RLock

from app.domain.models import VM, VMStatus


class InMemoryVMRepo:
    def __init__(self) -> None:
        self._lock = RLock()
        self._vms: dict[str, VM] = {}

    def create(self, vm: VM) -> VM:
        with self._lock:
            self._vms[vm.id] = vm
            return vm

    def get(self, vm_id: str) -> VM | None:
        with self._lock:
            return self._vms.get(vm_id)

    def update(self, vm: VM) -> VM:
        with self._lock:
            if vm.id not in self._vms:
                raise KeyError(vm.id)
            self._vms[vm.id] = vm
            return vm

    def list(self, status: VMStatus | None = None) -> Iterable[VM]:
        with self._lock:
            values = list(self._vms.values())
        if status is None:
            return values
        return [v for v in values if v.status == status]

    def delete(self, vm_id: str) -> None:
        with self._lock:
            self._vms.pop(vm_id, None)

    def mark_deleted(self, vm_id: str) -> VM:
        with self._lock:
            vm = self._vms.get(vm_id)
            if vm is None:
                raise KeyError(vm_id)
            vm = replace(vm, status=VMStatus.DELETED)
            self._vms[vm_id] = vm
            return vm
