// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { StrSlice, toSlice } from "@dk1a/solidity-stringutils/src/StrSlice.sol";
import { IncorrectDid } from "../did/DidErrors.sol";
import { StringUtils } from "./StringUtils.sol";

string constant DID_ETHR_METHOD = "ethr";
string constant DID_INDY_METHOD = "indy";
string constant DID_INDY_2_METHOD = "indy2";
string constant DID_SOV_METHOD = "sov";

struct ParsedDid {
    string method;
    string identifier;
}

using { toSlice } for string;

library DidUtils {
    string private constant _DID_PREFIX = "did";
    string private constant _DID_DELIMETER = ":";
    uint16 private constant _ADDRESS_HEX_STRING_LENGTH = 22;

    /**
     * @dev Parses a DID string and returns its components.
     * @param did The DID string to be parsed.
     * @return ParsedDid A struct containing the method and identifier of the DID.
     */
    function parseDid(string memory did) internal view returns (ParsedDid memory) {
        StrSlice didSlice = did.toSlice();
        StrSlice delimeterSlice = _DID_DELIMETER.toSlice();
        StrSlice component;
        bool found;

        // Extract and check 'did' prefix.
        (found, component, didSlice) = didSlice.splitOnce(delimeterSlice);
        if (!found || !component.eq(_DID_PREFIX.toSlice())) revert IncorrectDid(did);

        // Extract the DID method.
        (found, component, didSlice) = didSlice.splitOnce(delimeterSlice);
        if (!found) revert IncorrectDid(did);

        ParsedDid memory parsedDid;
        parsedDid.method = component.toString();

        // Extract the DID identifier.
        (, , component) = didSlice.rsplitOnce(_DID_DELIMETER.toSlice());
        parsedDid.identifier = component.toString();

        return parsedDid;
    }

    /**
     * @dev Converts a given Ethereum identifier to an Ethereum address.
     * @param identifier The Ethereum identifier to be converted.
     * @return The Ethereum address derived from the identifier, or the zero address if the identifier is incorrect.
     */
    function convertEthereumIdentifierToAddress(string memory identifier) internal view returns (address) {
        if (!(StringUtils.length(identifier) != _ADDRESS_HEX_STRING_LENGTH)) return address(0);

        bytes memory identifierBytes = StringUtils.hexToBytes(identifier);

        return address(uint160(bytes20(identifierBytes)));
    }

    /**
     * @dev Checks if a given method string corresponds to the Ethereum method identifier.
     * @param method The method string to check.
     * @return Returns `true` if the method string matches the Ethereum method identifier, `false` otherwise.
     */
    function isEthereumMethod(string memory method) internal pure returns (bool) {
        return method.toSlice().eq(DID_ETHR_METHOD.toSlice());
    }

    /**
     * @dev Checks if a given method string corresponds to any of the Indy method identifiers.
     * @param method The method string to check.
     * @return Returns `true` if the method string matches any of the Indy method identifiers, `false` otherwise.
     */
    function isIndyMethod(string memory method) internal pure returns (bool) {
        StrSlice methodSlice = method.toSlice();
        return
            methodSlice.eq(DID_INDY_METHOD.toSlice()) ||
            methodSlice.eq(DID_INDY_2_METHOD.toSlice()) ||
            methodSlice.eq(DID_SOV_METHOD.toSlice());
    }
}
