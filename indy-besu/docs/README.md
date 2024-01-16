## Design documents

### Modules

- Network Permission modules:
  - [Auth](design/auth.md) - control user permissions
    - role control - manage roles assigned to accounts  
    - access control - first level validation: whether to accept write transactions (execute target contract method) from a given account
  - [Upgrading contracts](design/upgradability.md) - control versions of deployed contracts (proposing and approving new versions).
  - [Validators node management](design/network.md) - control the list of network validator nodes
- [DID Methods](design/did-registry.md) - Supported DID methods 
- Registries:
  - [DID Document Registry](design/did-registry.md)
  - [CL Registry](design/cl-registry.md)
- [VDR](design/vdr.md) - design of VDR library
 
## Migration documents

- [Indy Migration](migrtion/migration.md)
