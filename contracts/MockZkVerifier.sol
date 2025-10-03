// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./ITEERegistry.sol";

contract MockZkVerifier {
    ITEERegistry public teeRegistry;

    constructor(address _teeRegistry) {
        teeRegistry = ITEERegistry(_teeRegistry);
    }

    function verifyAndRegister(
        uint256 agentId,
        string calldata teeArch,
        bytes32 codeMeasurement,
        bytes calldata pubkey,
        bytes calldata attestation
    ) external returns (uint256) {
        // Mock: In production, verify ZK proof of attestation here
        require(attestation.length > 0, "Empty attestation");

        // Register in TEE Registry
        return teeRegistry.registerTEEKey(
            agentId,
            teeArch,
            codeMeasurement,
            pubkey,
            attestation
        );
    }
}
