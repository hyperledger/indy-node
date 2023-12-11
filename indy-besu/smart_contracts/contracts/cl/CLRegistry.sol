// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import { DidNotFound, IncorrectDid } from "../did/DidErrors.sol";
import { DidMetadata } from "../did/DidTypes.sol";
import { UniversalDidResolverInterface } from "../did/UniversalDidResolverInterface.sol";
import { Errors } from "../utils/Errors.sol";
import { InvalidIssuerId, IssuerHasBeenDeactivated, IssuerNotFound, SenderIsNotIssuerDidOwner } from "./ClErrors.sol";

contract CLRegistry {
    /**
     * @dev Reference to the contract that resolves DIDs
     */
    UniversalDidResolverInterface internal _didResolver;

    /**
     * @dev Check that the Issuer DID exist, controlled by sender, and active.
     * @param id The Issuer's DID.
     */
    modifier _validIssuer(string memory id) {
        try _didResolver.resolveMetadata(id) returns (DidMetadata memory metadata) {
            if (msg.sender != metadata.creator) {
                revert SenderIsNotIssuerDidOwner(msg.sender, metadata.creator);
            }
            if (metadata.deactivated) revert IssuerHasBeenDeactivated(id);
        } catch (bytes memory reason) {
            if (Errors.equals(reason, DidNotFound.selector)) revert IssuerNotFound(id);
            if (Errors.equals(reason, IncorrectDid.selector)) revert InvalidIssuerId(id);

            Errors.rethrow(reason);
        }
        _;
    }
}
