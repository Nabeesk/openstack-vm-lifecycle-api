from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.models import VM, VMSpec, VMStatus


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict | None = None


class VMCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    image: str = Field(min_length=1, max_length=120)
    flavor: str = Field(min_length=1, max_length=120)
    network: str = Field(min_length=1, max_length=120)

    def to_spec(self) -> VMSpec:
        return VMSpec(name=self.name, image=self.image, flavor=self.flavor, network=self.network)


class VMResponse(BaseModel):
    id: str
    name: str
    image: str
    flavor: str
    network: str
    status: VMStatus
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_domain(vm: VM) -> VMResponse:
        return VMResponse(
            id=vm.id,
            name=vm.spec.name,
            image=vm.spec.image,
            flavor=vm.spec.flavor,
            network=vm.spec.network,
            status=vm.status,
            created_at=vm.created_at,
            updated_at=vm.updated_at,
        )


class VMListResponse(BaseModel):
    items: list[VMResponse]


class RebootRequest(BaseModel):
    type: Literal["soft", "hard"] = "soft"

    @property
    def hard(self) -> bool:
        return self.type == "hard"


class ResizeRequest(BaseModel):
    new_flavor: str = Field(min_length=1, max_length=120)
