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
        address ethereumDIDRegistryAddress,
        address didRegistryddress,
        address upgradeControlAddress
    ) public reinitializer(1) {
        _ethereumDIDRegistry = EthereumDIDRegistry(ethereumDIDRegistryAddress);
        _didRegistry = DidRegistryInterface(didRegistryddress);
        _initializeUpgradeControl(upgradeControlAddress);
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
        return _hexToAddress(suffix.toString());
    }

    function _hexToAddress(string memory hexString) internal pure returns (address) {
        bytes memory bytesArray = new bytes(20);
        for (uint256 i = 0; i < 20; i++) {
            uint8 byteValue = uint8(_hexCharToByte(hexString, 2 * i) * 16 + _hexCharToByte(hexString, 2 * i + 1));
            bytesArray[i] = bytes1(byteValue);
        }
        return address(bytes20(bytesArray));
    }

    function _hexCharToByte(string memory s, uint256 index) internal pure returns (uint8) {
        bytes1 hexChar = bytes(s)[index];
        if (hexChar >= 0x30 && hexChar <= 0x39) {
            // ascii 0-9
            return uint8(hexChar) - 0x30;
        } else if (hexChar >= 0x61 && hexChar <= 0x66) {
            // ascii a-f
            return uint8(hexChar) - 0x57;
        } else if (hexChar >= 0x41 && hexChar <= 0x46) {
            // ascii A-F
            return uint8(hexChar) - 0x37;
        } else {
            revert("Invalid hexadecimal character.");
        }
    }
}
