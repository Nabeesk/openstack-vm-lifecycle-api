from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4


class VMStatus(str, Enum):
    BUILD = "BUILD"
    ACTIVE = "ACTIVE"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
    DELETED = "DELETED"


@dataclass(frozen=True)
class VMSpec:
    name: str
    image: str
    flavor: str
    network: str


@dataclass
class VM:
    id: str
    spec: VMSpec
    status: VMStatus = VMStatus.BUILD
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @staticmethod
    def new(spec: VMSpec) -> VM:
        now = datetime.now(timezone.utc)
        return VM(id=str(uuid4()), spec=spec, status=VMStatus.BUILD, created_at=now, updated_at=now)
