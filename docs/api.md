 ## API summary
 
 Base path: `/v1`
 
 ### Create VM
 - `POST /vms`
 
 Request body:
 - `name`, `image`, `flavor`, `network`
 
 ### List VMs
 - `GET /vms`
 - Optional query: `status` (one of `BUILD`, `ACTIVE`, `STOPPED`, `ERROR`, `DELETED`)
 
 ### Get VM
 - `GET /vms/{vm_id}`
 
 ### Start VM
 - `POST /vms/{vm_id}/start`
 
 ### Stop VM
 - `POST /vms/{vm_id}/stop`
 
 ### Reboot VM
 - `POST /vms/{vm_id}/reboot`
 
 Request body:
 - `type`: `"soft"` or `"hard"`
 
 ### Resize VM
 - `POST /vms/{vm_id}/resize`
 
 Request body:
 - `new_flavor`
 
 ### Delete VM
 - `DELETE /vms/{vm_id}`
 
 ### Health check
 - `GET /healthz`
 
 ## Error format
 Non-2xx responses use:
 
 ```json
 {
   "error": "not_found | invalid_transition | driver_error",
   "message": "human readable message",
   "details": { "optional": "metadata" }
 }
 ```
 
 ## Notes
 - This PoC uses an in-memory store; restart the server to reset state.
 - `DELETED` VMs are hidden from list results and will return 404 on `GET`.
