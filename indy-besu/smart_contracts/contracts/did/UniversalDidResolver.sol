// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { EthereumDIDRegistry } from "ethr-did-registry/contracts/EthereumDIDRegistry.sol";

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";
import { UnsupportedOperation } from "../utils/Errors.sol";
import { DidRegistryInterface } from "./DidRegistryInterface.sol";
import { DidDocument, DidMetadata } from "./DidTypes.sol";
import { UniversalDidResolverInterface } from "./UniversalDidResolverInterface.sol";

using { toSlice } for string;

contract UniversalDidResolver is UniversalDidResolverInterface, ControlledUpgradeable {
    string internal constant _ETHR_DID_PREFIX = "did:ethr";
    string internal constant _DID_DELIMETER = ":";

    DidRegistryInterface internal _didRegistry;
    EthereumDIDRegistry internal _ethereumDIDRegistry;

    function initialize(
        address upgradeControlAddress,
        address didRegistryddress,
        address ethereumDIDRegistryAddress
    ) public reinitializer(1) {
        _initializeUpgradeControl(upgradeControlAddress);
        _didRegistry = DidRegistryInterface(didRegistryddress);
        _ethereumDIDRegistry = EthereumDIDRegistry(ethereumDIDRegistryAddress);
    }

    /// @inheritdoc UniversalDidResolverInterface
    function resolveDocument(string memory id) public view override returns (DidDocument memory document) {
        if (id.toSlice().startsWith(_ETHR_DID_PREFIX.toSlice())) {
            revert UnsupportedOperation("UniversalDidResolver.resolveDocument", "Unsupported DID Method: 'ethr'");
        } else {
            return _didRegistry.resolveDid(id).document;
        }
    }

    /// @inheritdoc UniversalDidResolverInterface
    function resolveMetadata(string memory id) public view override returns (DidMetadata memory metadata) {
        if (id.toSlice().startsWith(_ETHR_DID_PREFIX.toSlice())) {
            address identity = _extractIdentityFromDidEthr(id);
            address identityOwner = _ethereumDIDRegistry.identityOwner(identity);
            return DidMetadata(identityOwner, 0, 0, false);
        } else {
            return _didRegistry.resolveDid(id).metadata;
        }
    }

    function _extractIdentityFromDidEthr(string memory id) internal view returns (address) {
        (, , StrSlice suffix) = id.toSlice().rsplitOnce(_DID_DELIMETER.toSlice());
        return address(bytes20(bytes(suffix.toString())));
    }
}
