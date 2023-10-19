// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

error AuthenticationKeyRequired(string did);
error AuthenticationKeyNotFound(string id);
error DidNotFound(string did);
error DidAlreadyExist(string did);
error DidHasBeenDeactivated(string did);
error IncorrectDid(string did);
