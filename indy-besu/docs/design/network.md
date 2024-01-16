# Validators node management

## Storage format

* Validators list:
    * Description: List of current validator node addresses
    * Format:
        ```
        address[] validators;
        ```
    * Example:
      ```
      [
          "0x93917cadbace5dfce132b991732c6cda9bcc5b8a",
          "0x27a97c9aaf04f18f3014c32e036dd0ac76da5f18",  
          "0xce412f988377e31f4d0ff12d74df73b51c42d0ca"  
          ...
      ]
      ```
* Validators details:
    * Description: Mapping holding information about validator nodes
    * Format:
        ```
        mapping(address validatorAddress => ValidatorInfo validatorInfo);

        struct ValidatorInfo {
            address account; // validator owner accoutn address
            uint8 validatorIndex; // index of valdiator in the array
        }
        ```
      * Example:
        ```
        {
            "0x93917cadbace5dfce132b991732c6cda9bcc5b8a": {
                "account": "0xed9d02e382b34818e88b88a309c7fe71e65f419d",
                "validatorIndex": 0
            },
            "0x27a97c9aaf04f18f3014c32e036dd0ac76da5f18": {
                "account": "0xb30f304642de3fee4365ed5cd06ea2e69d3fd0ca",
                "validatorIndex": 1
            },
            ...
        }
        ```

## Transactions (Smart Contract's methods)

Contract name: **ValidatorControl**

### Get Validators

* Method: `getValidators`
    * Description: Transaction to get the list of current validator nodes.
    * Restrictions: None
    * Format
        ```
        ValidatorControl.getValidators() returns (address[] validators)
        ```
    * Example:
        ```
        ValidatorControl.removeValidator()
        ```
    * Raised Event: None

### Add Validator

* Method: `addValidator`
    * Description: Transaction to add a new validator node into validator's list. Sender will be set as an owner of the validator node. 
    * Restrictions:
    * Sender must have STEWARD role assigned
    * Sender must not have existing validator 
    * Validator must be unique
    * Number of validator cannot be greater than 256
    * Format
        ```
        ValidatorControl.addValidator(
        address newValidator
        )
        ```
    * Example:
        ```
        ValidatorControl.addValidator(
        "0x98c1334496614aed49d2e81526d089f7264fed9c"
        )
        ```
    * Raised Event:
        * ValidatorAdded(validatorAddress, ownerAddress, numberOfValidators)

### Remove Validator

* Method: `removeValidator`
    * Description: Transaction to remove validator node from validator's list.
    * Restrictions:
        * Sender must have STEWARD role assigned
        * Should leave at least one validator after deletion
        * Validator should exist
    * Format
        ```
        ValidatorControl.removeValidator(
        address validator
        )
        ```
    * Example:
        ```
        ValidatorControl.removeValidator(
        "0x98c1334496614aed49d2e81526d089f7264fed9c"
        )
        ```
    * Raised Event:
        * ValidatorRemoved(validatorAddress, ownerAddress, numberOfValidators)
