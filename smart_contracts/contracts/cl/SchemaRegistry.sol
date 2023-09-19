// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { SchemaRegistryInterface } from "./SchemaRegistryInterface.sol";
import "../auth/RoleControl.sol";

contract SchemaRegistry is SchemaRegistryInterface {
    mapping(string id => Schema schema) private _schemas;

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

    function create(string calldata id, Schema calldata schema) public virtual senderIsTrustee returns (string memory outId) {
        _schemas[id] = schema;
        return id;
    }

    function resolve(string calldata id) public view virtual returns (Schema memory schema) {
        return _schemas[id];
    }
}
