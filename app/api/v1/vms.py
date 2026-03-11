from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.domain.models import VMStatus
from app.drivers.mock_openstack import MockOpenStackDriver
from app.repo.inmemory import InMemoryVMRepo
from app.schemas import (
    ErrorResponse,
    RebootRequest,
    ResizeRequest,
    VMCreateRequest,
    VMListResponse,
    VMResponse,
)
from app.services.errors import DriverError, InvalidTransitionError, VMNotFoundError
from app.services.vm_service import VMService

router = APIRouter(tags=["vms"])

_repo = InMemoryVMRepo()
_driver = MockOpenStackDriver()
_service = VMService(_repo, _driver)


def get_vm_service() -> VMService:
    return _service


def _error(status_code: int, *, error: str, message: str, details: dict | None = None) -> JSONResponse:
    payload = ErrorResponse(error=error, message=message, details=details).model_dump()
    return JSONResponse(status_code=status_code, content=payload)


@router.post("/vms", response_model=VMResponse, responses={502: {"model": ErrorResponse}})
def create_vm(body: VMCreateRequest, svc: VMService = Depends(get_vm_service)) -> VMResponse | JSONResponse:
    try:
        vm = svc.create(body.to_spec())
        return VMResponse.from_domain(vm)
    except DriverError as e:
        return _error(502, error="driver_error", message=str(e))


@router.get("/vms", response_model=VMListResponse)
def list_vms(
    status: VMStatus | None = Query(default=None, description="Optional status filter (e.g. ACTIVE, STOPPED)"),
    svc: VMService = Depends(get_vm_service),
) -> VMListResponse:
    vms = svc.list(status=status)
    return VMListResponse(items=[VMResponse.from_domain(v) for v in vms])


@router.get("/vms/{vm_id}", response_model=VMResponse, responses={404: {"model": ErrorResponse}})
def get_vm(vm_id: str, svc: VMService = Depends(get_vm_service)) -> VMResponse | JSONResponse:
    try:
        return VMResponse.from_domain(svc.get(vm_id))
    except VMNotFoundError as e:
        return _error(404, error="not_found", message=str(e), details={"vm_id": e.vm_id})


@router.post(
    "/vms/{vm_id}/start",
    response_model=VMResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def start_vm(vm_id: str, svc: VMService = Depends(get_vm_service)) -> VMResponse | JSONResponse:
    try:
        return VMResponse.from_domain(svc.start(vm_id))
    except VMNotFoundError as e:
        return _error(404, error="not_found", message=str(e), details={"vm_id": e.vm_id})
    except InvalidTransitionError as e:
        return _error(409, error="invalid_transition", message=str(e), details={"status": e.status, "action": e.action})
    except DriverError as e:
        return _error(502, error="driver_error", message=str(e))


@router.post(
    "/vms/{vm_id}/stop",
    response_model=VMResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def stop_vm(vm_id: str, svc: VMService = Depends(get_vm_service)) -> VMResponse | JSONResponse:
    try:
        return VMResponse.from_domain(svc.stop(vm_id))
    except VMNotFoundError as e:
        return _error(404, error="not_found", message=str(e), details={"vm_id": e.vm_id})
    except InvalidTransitionError as e:
        return _error(409, error="invalid_transition", message=str(e), details={"status": e.status, "action": e.action})
    except DriverError as e:
        return _error(502, error="driver_error", message=str(e))


@router.post(
    "/vms/{vm_id}/reboot",
    response_model=VMResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def reboot_vm(
    vm_id: str,
    body: RebootRequest,
    svc: VMService = Depends(get_vm_service),
) -> VMResponse | JSONResponse:
    try:
        return VMResponse.from_domain(svc.reboot(vm_id, hard=body.hard))
    except VMNotFoundError as e:
        return _error(404, error="not_found", message=str(e), details={"vm_id": e.vm_id})
    except InvalidTransitionError as e:
        return _error(409, error="invalid_transition", message=str(e), details={"status": e.status, "action": e.action})
    except DriverError as e:
        return _error(502, error="driver_error", message=str(e))


@router.post(
    "/vms/{vm_id}/resize",
    response_model=VMResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def resize_vm(
    vm_id: str,
    body: ResizeRequest,
    svc: VMService = Depends(get_vm_service),
) -> VMResponse | JSONResponse:
    try:
        return VMResponse.from_domain(svc.resize(vm_id, new_flavor=body.new_flavor))
    except VMNotFoundError as e:
        return _error(404, error="not_found", message=str(e), details={"vm_id": e.vm_id})
    except InvalidTransitionError as e:
        return _error(409, error="invalid_transition", message=str(e), details={"status": e.status, "action": e.action})
    except DriverError as e:
        return _error(502, error="driver_error", message=str(e))


@router.delete(
    "/vms/{vm_id}",
    response_model=VMResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def delete_vm(vm_id: str, svc: VMService = Depends(get_vm_service)) -> VMResponse | JSONResponse:
    try:
        return VMResponse.from_domain(svc.delete(vm_id))
    except VMNotFoundError as e:
        return _error(404, error="not_found", message=str(e), details={"vm_id": e.vm_id})
    except InvalidTransitionError as e:
        return _error(409, error="invalid_transition", message=str(e), details={"status": e.status, "action": e.action})
    except DriverError as e:
        return _error(502, error="driver_error", message=str(e))
