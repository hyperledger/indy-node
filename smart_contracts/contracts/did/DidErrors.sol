// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

/**
 * @dev Error that thrown when an authentication key is not provided in the DID Document.
 */
error AuthenticationKeyRequired(string did);

/**
 * @dev Error that thrown when the specified authentication key is not found in the DID Document.
 */
error AuthenticationKeyNotFound(string id);

/**
 * @dev Error that thrown when the specified DID is not found.
 */
error DidNotFound(string did);

/**
 * @dev Error that thrown when an attempt is made to create a DID that already exists.
 */
error DidAlreadyExist(string did);

/**
 * @dev Error that thrown when an operation is attempted on a DID that has been deactivated.
 */
error DidHasBeenDeactivated(string did);

/**
 * @dev Error that thrown when a DID provided is incorrect.
 */
error IncorrectDid(string did);

