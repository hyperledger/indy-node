## Auth model

### Roles

| Label    | Value     |
|----------|-----------|
| Trustee  | 1         |
| Endorser | 2         |
| Steward  | 3         |

### Account role management

| Contract    | Method     | Value      | Required Role | Action Description                       |
|-------------|------------|------------|---------------|------------------------------------------|
| RoleControl | hasRole    | -          | any           | Check if an account has a requested role |
| RoleControl | getRole    | -          | any           | Get account role                         |
| RoleControl | assignRole | Trustee    | Trustee       | Assign Trustee role to an account        |
| RoleControl | assignRole | Endorser   | Trustee       | Assign Endorser role to an account       |
| RoleControl | assignRole | Steward    | Trustee       | Assign Steward role to an account        |
| RoleControl | revokeRole | Trustee    | Trustee       | Revoke Trustee role from an account      |
| RoleControl | revokeRole | Endorser   | Trustee       | Assign Endorser role to an account       |
| RoleControl | revokeRole | Steward    | Trustee       | Assign Steward role to an account        |

### Validator nodes management

| Contract         | Method          | Required Role | Action Description                      |
|------------------|-----------------|---------------|-----------------------------------------|
| ValidatorControl | getValidators   | any           | Get the list of current validator nodes |
| ValidatorControl | addValidator    | Steward       | Add new validator node                  |
| ValidatorControl | removeValidator | Steward       | Remove validator node                   |


### DID Document management

| Contract      | Method        | Required Role | Action Description              |
|---------------|---------------|---------------|---------------------------------|
| DidRegistry   | createDid     | any           | Create a new DID Document       |
| DidRegistry   | updateDid     | DID owner     | Update DID an existing Document |
| DidRegistry   | deactivateDid | DID owner     | Deactivate an existing DID      |
| DidRegistry   | resolve       | any           | Resolve DID Document for a DID  |


### CL Registry management

| Contract                     | Method  | Required Role | Action Description                   |
|------------------------------|---------|---------------|--------------------------------------|
| SchemaRegistry               | create  | any           | Create a new Schema                  |
| SchemaRegistry               | resolve | any           | Resolve Schema by id                 |
| CredentialDefinitionRegistry | create  | any           | Create a new Credential Definition   |
| CredentialDefinitionRegistry | resolve | any           | Resolve Credential Definition by id  |


## Storage format

* Roles collection:
  * Description: Mapping holding the list of accounts with roles assigned to them. Accounts which does not have any role assigned are not present in the list. 
  * Format:
      ```
      Map<address account, number role>
      ```
  * Example: 
    ```
    {
        account_addres_1: 1,
        account_addres_2: 1,
        account_addres_3: 3,
        ...
    }
    ```

* Roles owners:
  * Description: Mapping holding relationship between existing roles and roles who can manage (assign/revoke) them. 
  * Format:
      ```
      Map<number role, number ownerRole>
      ```
  * Example: 
    ```
    {
        1: 1,
        2: 1,
        3: 1,
        ...
    }
    ```
