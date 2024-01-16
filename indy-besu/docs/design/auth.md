# Auth model

## Role control

Contract to manage roles assigned to accounts.

### Roles

| Label              | Value                                  |
|--------------------|----------------------------------------|
| Trustee            | 1                                      |
| Endorser           | 2                                      |
| Steward            | 3                                      |
| User without role  | 0 / "null" (not present on the ledger) |

### Storage format

* Roles collection:
  * Description: Mapping holding the list of accounts with roles assigned to them. Accounts which does not have any role assigned are not present in the list. 
  * Format:
      ```
      mapping(address account => ROLES role);
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
      mapping(ROLES role => ROLES ownerRole);
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
  
### Transactions (Smart Contract's methods)

Contract name: **RoleControl**

#### Check if account has role assigned

* Method: `hasRole`
  * Description: Transaction to check if an account has requested role assigned.
  * Restrictions: None
  * Format
      ```
      RoleControl.hasRole(
        ROLES role,
        address account
      ) returns (bool)
      ```
  * Example:
      ```
      RoleControl.hasRole(
        ROLES.TRUSTEE,  
        "0xfe3b557e8fb62b89f4916b721be55ceb828dbd73"
      )
      ```
  * Raised Event: None

#### Get account role

* Method: `getRole`
  * Description: Transaction to get the role assigned to an account 
  * Restrictions: None
  * Format:
      ```
      RoleControl.getRole(
        address account
      ) returns (ROLES)
      ```
  * Example:
      ```
      RoleControl.getRole(
        "0xfe3b557e8fb62b89f4916b721be55ceb828dbd73"
      )
      ```
  * Raised Event: None

#### Assign role to an account 

* Method: `assignRole`
  * Description: Transaction to assign role to an account
  * Restrictions: 
    * Sender must have assigned role owning the target role - for example be default TRUSTEE owns ENDORSER role. In order to assign ENDORSER role to an account sender must have TRUSTEE role.  
  * Format:
      ```
      RoleControl.assignRole(
        ROLES role,
        address account
      )
      ```
  * Example:
      ```
      RoleControl.assignRole(
        ROLES.TRUSTEE,
        "0xfe3b557e8fb62b89f4916b721be55ceb828dbd73"
      )
  * Raised Event: 
    * RoleAssigned(ROLE, account, sender)

#### Revoke role from an account 

* Method: `revokeRole`
  * Description: Transaction to revive role from an account
  * Restrictions: 
    * Sender must have assigned role owning the target role - for example be default TRUSTEE owns ENDORSER role. In order to revoke ENDORSER role to an account sender must have TRUSTEE role.  
  * Format:
      ```
      RoleControl.revokeRole(
        ROLES role,
        address account
      )
      ```
  * Example:
      ```
      RoleControl.revokeRole(
        ROLES.TRUSTEE,
        "0xfe3b557e8fb62b89f4916b721be55ceb828dbd73"
      )
  * Raised Event: 
    * RoleRevoked(ROLE, account, sender)



## Access control

The first level validation whether to accept write transactions (execute target contract method) from a given account or not.

### Transactions (Smart Contract's methods)

Contract name: **transactionAllowed**

#### Check if sender can perform an action

* Method: `transactionAllowed`
  * Description: Transaction to check whether to accept a transaction received from a given account.
  * Restrictions: None
  * Format
      ```
      AccountControl.transactionAllowed(
        address sender,
        address target,
        uint256 value,
        uint256 gasPrice,
        uint256 gasLimit,
        bytes calldata payload
      ) returns (bool)
      ```
  * Raised Event: None

## Ledger Permissions

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

| Contract          | Method                         | Required Role               | Action Description              |
|-------------------|--------------------------------|-----------------------------|---------------------------------|
| IndyDidRegistry   | createDid                      | Trustee, Endorser, Steward  | Create a new DID Document       |
| IndyDidRegistry   | updateDid                      | DID owner                   | Update DID an existing Document |
| IndyDidRegistry   | deactivateDid                  | DID owner                   | Deactivate an existing DID      |
| IndyDidRegistry   | resolveDid                     | any                         | Resolve DID Document for a DID  |

### CL Registry management

| Contract                     | Method                      | Required Role               | Action Description                       |
|------------------------------|-----------------------------|-----------------------------|------------------------------------------|
| SchemaRegistry               | createSchema                | Trustee, Endorser, Steward  | Create a new Schema                      |
| SchemaRegistry               | resolveSchema               | any                         | Resolve Schema by id                     |
| CredentialDefinitionRegistry | createCredentialDefinition  | Trustee, Endorser, Steward  | Create a new Credential Definition       |
| CredentialDefinitionRegistry | resolveCredentialDefinition | any                         | Resolve Credential Definition by id      |

### Contract upgrade management

| Contract          | Method                    | Required Role     | Action Description                                                       |
|-------------------|---------------------------|-------------------|--------------------------------------------------------------------------|
| UpgradeControl    | propose                   | Trustee           | Propose the upgrade of a specefic contract implementation                |
| UpgradeControl    | approve                   | Trustee           | Approve the upgrade of a specefic contract implementation                |
| UpgradeControl    | ensureSufficientApprovals | any               | Ensures that an implementation upgrade has received sufficient approvals |

### General transactions management

| Transaction              | Required Role                          | Action Description                               |
|--------------------------|----------------------------------------|--------------------------------------------------|
| Deploy contract          | Trustee                                | Deploy a new contract                            |
| Modify contract state    | Per contract method as described above | Execute contract method to modify its state      |
| Read contract state      | any                                    | Execute contract method to read its state        |
