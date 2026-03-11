from __future__ import annotations


class VMNotFoundError(Exception):
    def __init__(self, vm_id: str) -> None:
        super().__init__(f"VM '{vm_id}' not found")
        self.vm_id = vm_id


class InvalidTransitionError(Exception):
    def __init__(self, vm_id: str, action: str, status: str) -> None:
        super().__init__(f"Cannot '{action}' VM '{vm_id}' when status is {status}")
        self.vm_id = vm_id
        self.action = action
        self.status = status


class DriverError(Exception):
    pass
