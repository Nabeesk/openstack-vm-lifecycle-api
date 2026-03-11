 ## Architecture & design choices
 
 ### Scope (timebox-driven)
 This prototype focuses on **API design and lifecycle logic**. It intentionally avoids “production complexity” (real OpenStack, persistence, async workers) while keeping extension points clear.
 
 ### High-level flow
 - Request hits **FastAPI** endpoint (`app/api/v1/vms.py`)
 - Endpoint validates payload (Pydantic models in `app/schemas.py`)
 - Endpoint calls **service layer** (`app/services/vm_service.py`)
 - Service layer:
   - Loads/updates VM from **repository** (`app/repo/inmemory.py`)
   - Calls **compute driver** (`app/drivers/base.py`) to simulate OpenStack action
   - Enforces lifecycle transition rules and returns updated VM
 
 ### Layers and responsibilities
 - **API layer**: HTTP, validation, error mapping to status codes
 - **Service layer**: lifecycle rules, idempotency for start/stop, orchestration
 - **Repo**: store and retrieve VM objects (in-memory for simplicity)
 - **Driver**: boundary for compute actions. Today it’s a mock; later it can be a real OpenStack driver.
 
 ### State machine (simplified)
 - Create: `BUILD -> ACTIVE` (or `ERROR` if driver fails)
 - Stop: `ACTIVE -> STOPPED` (idempotent if already STOPPED)
 - Start: `STOPPED -> ACTIVE` (idempotent if already ACTIVE)
 - Reboot: allowed only when `ACTIVE`
 - Resize: allowed only when `STOPPED`
 - Delete: marks VM as `DELETED` and hides it from list; subsequent `GET` returns 404
 
 ### Error handling
 - **404**: VM not found (or already deleted)
 - **409**: invalid lifecycle transition (ex: resize while ACTIVE)
 - **502**: compute driver failure (simulates external dependency failure)
 - **422**: request validation errors (Pydantic/FastAPI default)
 
 ### Extending to real OpenStack (future)
Replace `MockOpenStackDriver` with an `OpenStackSDKDriver` implementation of `ComputeDriver` using `openstacksdk`.
 The API surface and service layer should remain stable; only the driver boundary changes.
