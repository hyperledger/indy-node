// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

struct CredentialDefinition {
    CredentialDefinitionData data;
    CredentialDefinitionMetadata metadata;
}

struct CredentialDefinitionData {
    string id;
    string issuerId;
    string schemaId;
    string entityType;
    string tag;
    string value;
}

struct CredentialDefinitionMetadata {
    uint256 created;
}