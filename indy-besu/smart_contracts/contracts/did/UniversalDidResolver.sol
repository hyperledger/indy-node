// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { EthereumDIDRegistry } from "ethr-did-registry/contracts/EthereumDIDRegistry.sol";

import { ControlledUpgradeable } from "../upgrade/ControlledUpgradeable.sol";
import { UnsupportedOperation } from "../utils/Errors.sol";
import { IncorrectDid } from "./DidErrors.sol";
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

            if (identity == address(0)) revert IncorrectDid(id);

            address identityOwner = _ethereumDIDRegistry.identityOwner(identity);
            return DidMetadata(identityOwner, 0, 0, false);
        } else {
            return _didRegistry.resolveDid(id).metadata;
        }
    }

    function _extractIdentityFromDidEthr(string memory id) internal view returns (address) {
        (, , StrSlice suffix) = id.toSlice().rsplitOnce(_DID_DELIMETER.toSlice());
        return _hexToAddress(suffix.toString());
    }

    function _hexToAddress(string memory hexString) internal pure returns (address) {
        if (bytes(hexString).length != 40) return address(0);

        bytes memory bytesArray = new bytes(20);
        for (uint256 i = 0; i < 20; i++) {
            (uint8 firstByte, bool firstByteValid) = _hexCharToByte(hexString, 2 * i);
            if (!firstByteValid) return address(0);

            (uint8 secondByte, bool secondByteValid) = _hexCharToByte(hexString, 2 * i + 1);
            if (!secondByteValid) return address(0);

            bytesArray[i] = bytes1(firstByte * 16 + secondByte);
        }
        return address(bytes20(bytesArray));
    }

    function _hexCharToByte(string memory s, uint256 index) internal pure returns (uint8, bool) {
        bytes1 hexChar = bytes(s)[index];
        if (hexChar >= 0x30 && hexChar <= 0x39) {
            // ascii 0-9
            return (uint8(hexChar) - 0x30, true);
        } else if (hexChar >= 0x61 && hexChar <= 0x66) {
            // ascii a-f
            return (uint8(hexChar) - 0x57, true);
        } else if (hexChar >= 0x41 && hexChar <= 0x46) {
            // ascii A-F
            return (uint8(hexChar) - 0x37, true);
        } else {
            return (0, false);
        }
    }
}
