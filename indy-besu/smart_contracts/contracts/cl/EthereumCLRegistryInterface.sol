// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface EthereumCLRegistryInterface {
    /**
     * @dev Event that is sent when a new CL resource created
     *
     * @param id Hash of resource identifier
     * @param resource Created resource as JSON string
     */
    event EthereumCLResourceCreated(bytes32 indexed id, string resource);

    /**
     * @dev Creates a new CL resource using event based approach.
     *
     * @param id Identifier of the resource.
     * @param resource The new AnonCreds resource as JSON string.
     */
    function createResource(string calldata id, string calldata resource) external;
}
