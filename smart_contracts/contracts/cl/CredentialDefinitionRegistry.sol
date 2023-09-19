// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { CredentialDefinitionRegistryInterface } from "./CredentialDefinitionRegistryInterface.sol";
import "../auth/RoleControl.sol";

contract CredentialDefinitionRegistry is CredentialDefinitionRegistryInterface {
    mapping(string id => CredentialDefinition credDef) private _credDefs;

    RoleControl private roleControl;

    constructor(address roleControlContractAddress) {
        roleControl = RoleControl(roleControlContractAddress);
    }

    modifier senderIsTrustee() {
        require(
            roleControl.hasRole(RoleControlInterface.ROLES.TRUSTEE, msg.sender),
            "Sender does not have TRUSTEE role assigned"
        );
        _;
    }

    function create(string calldata id, CredentialDefinition calldata credDef) public virtual senderIsTrustee returns (string memory outId) {
        _credDefs[id] = credDef;
        return id;
    }

    function resolve(string calldata id) public view virtual returns (CredentialDefinition memory credDef) {
        return _credDefs[id];
    }
}
