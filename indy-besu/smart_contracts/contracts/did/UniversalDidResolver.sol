// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";
import { UnsupportedOperation } from "../utils/Errors.sol";
import { DidUtils, ParsedDid } from "../utils/DidUtils.sol";
import { IncorrectDid } from "./DidErrors.sol";
import { IndyDidRegistryInterface } from "./IndyDidRegistryInterface.sol";
import { EthereumExtDidRegistry } from "./EthereumExtDidRegistry.sol";
import { DidDocument, DidMetadata } from "./DidTypes.sol";
import { UniversalDidResolverInterface } from "./UniversalDidResolverInterface.sol";

contract UniversalDidResolver is UniversalDidResolverInterface, ControlledUpgradeable {
    IndyDidRegistryInterface internal _indyDidRegistry;
    EthereumExtDidRegistry internal _ethereumDIDRegistry;

    function initialize(
        address upgradeControlAddress,
        address didRegistryddress,
        address ethereumDIDRegistryAddress
    ) public reinitializer(1) {
        _initializeUpgradeControl(upgradeControlAddress);
        _indyDidRegistry = IndyDidRegistryInterface(didRegistryddress);
        _ethereumDIDRegistry = EthereumExtDidRegistry(ethereumDIDRegistryAddress);
    }

    /// @inheritdoc UniversalDidResolverInterface
    function resolveDocument(string calldata id) public view override returns (DidDocument memory document) {
        ParsedDid memory parsedDid = DidUtils.parseDid(id);

        if (DidUtils.isIndyMethod(parsedDid.method)) {
            return _indyDidRegistry.resolveDid(id).document;
        } else {
            revert UnsupportedOperation(
                "UniversalDidResolver.resolveDocument",
                string.concat("Unsupported DID Method: '", parsedDid.method, "'")
            );
        }
    }

    /// @inheritdoc UniversalDidResolverInterface
    function resolveMetadata(string calldata id) public view override returns (DidMetadata memory metadata) {
        ParsedDid memory parsedDid = DidUtils.parseDid(id);

        if (DidUtils.isEthereumMethod(parsedDid.method)) {
            address identity = DidUtils.convertEthereumIdentifierToAddress(parsedDid.identifier);

            if (identity == address(0)) revert IncorrectDid(id);

            address identityOwner = _ethereumDIDRegistry.identityOwner(identity);
            return DidMetadata(identityOwner, 0, 0, false);
        } else if (DidUtils.isIndyMethod(parsedDid.method)) {
            return _indyDidRegistry.resolveDid(id).metadata;
        } else {
            revert UnsupportedOperation(
                "UniversalDidResolver.resolveMetadata",
                string.concat("Unsupported DID Method: '", parsedDid.method, "'")
            );
        }
    }
}
