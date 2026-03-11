from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from app.domain.models import VM, VMSpec, VMStatus
from app.drivers.base import ComputeDriver
from app.repo.inmemory import InMemoryVMRepo
from app.services.errors import DriverError, InvalidTransitionError, VMNotFoundError


class VMService:
    def __init__(self, repo: InMemoryVMRepo, driver: ComputeDriver) -> None:
        self._repo = repo
        self._driver = driver

    def create(self, spec: VMSpec) -> VM:
        vm = VM.new(spec)
        self._repo.create(vm)
        try:
            self._driver.provision(vm.id)
        except Exception as e:  # noqa: BLE001 - boundary converts driver failures
            vm = self._touch(replace(vm, status=VMStatus.ERROR))
            self._repo.update(vm)
            raise DriverError(str(e)) from e
        vm = self._touch(replace(vm, status=VMStatus.ACTIVE))
        self._repo.update(vm)
        return vm

    def get(self, vm_id: str) -> VM:
        vm = self._repo.get(vm_id)
        if vm is None or vm.status == VMStatus.DELETED:
            raise VMNotFoundError(vm_id)
        return vm

    def list(self, status: VMStatus | None = None) -> list[VM]:
        vms = list(self._repo.list(status=status))
        return [v for v in vms if v.status != VMStatus.DELETED]

    def start(self, vm_id: str) -> VM:
        vm = self.get(vm_id)
        if vm.status == VMStatus.ACTIVE:
            return vm
        if vm.status != VMStatus.STOPPED:
            raise InvalidTransitionError(vm_id, "start", vm.status.value)
        try:
            self._driver.start(vm_id)
        except Exception as e:  # noqa: BLE001
            raise DriverError(str(e)) from e
        vm = self._touch(replace(vm, status=VMStatus.ACTIVE))
        self._repo.update(vm)
        return vm

    def stop(self, vm_id: str) -> VM:
        vm = self.get(vm_id)
        if vm.status == VMStatus.STOPPED:
            return vm
        if vm.status != VMStatus.ACTIVE:
            raise InvalidTransitionError(vm_id, "stop", vm.status.value)
        try:
            self._driver.stop(vm_id)
        except Exception as e:  # noqa: BLE001
            raise DriverError(str(e)) from e
        vm = self._touch(replace(vm, status=VMStatus.STOPPED))
        self._repo.update(vm)
        return vm

    def reboot(self, vm_id: str, *, hard: bool) -> VM:
        vm = self.get(vm_id)
        if vm.status != VMStatus.ACTIVE:
            raise InvalidTransitionError(vm_id, "reboot", vm.status.value)
        try:
            self._driver.reboot(vm_id, hard=hard)
        except Exception as e:  # noqa: BLE001
            raise DriverError(str(e)) from e
        vm = self._touch(vm)
        self._repo.update(vm)
        return vm

    def resize(self, vm_id: str, *, new_flavor: str) -> VM:
        vm = self.get(vm_id)
        if vm.status != VMStatus.STOPPED:
            raise InvalidTransitionError(vm_id, "resize", vm.status.value)
        try:
            self._driver.resize(vm_id, new_flavor=new_flavor)
        except Exception as e:  # noqa: BLE001
            raise DriverError(str(e)) from e
        vm = self._touch(replace(vm, spec=replace(vm.spec, flavor=new_flavor)))
        self._repo.update(vm)
        return vm

    def delete(self, vm_id: str) -> VM:
        vm = self.get(vm_id)
        if vm.status == VMStatus.DELETED:
            raise VMNotFoundError(vm_id)
        if vm.status not in (VMStatus.ACTIVE, VMStatus.STOPPED, VMStatus.ERROR):
            raise InvalidTransitionError(vm_id, "delete", vm.status.value)
        try:
            self._driver.delete(vm_id)
        except Exception as e:  # noqa: BLE001
            raise DriverError(str(e)) from e
        vm = self._touch(replace(vm, status=VMStatus.DELETED))
        self._repo.update(vm)
        return vm

    @staticmethod
    def _touch(vm: VM) -> VM:
        return replace(vm, updated_at=datetime.now(timezone.utc))
