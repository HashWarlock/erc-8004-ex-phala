// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface ITEERegistry {
    struct TEEKey {
        uint256 agentId;
        string teeArch;
        bytes32 codeMeasurement;
        bytes pubkey;
        address verifier;
        uint256 timestamp;
    }

    event TEEKeyRegistered(
        uint256 indexed keyId,
        uint256 indexed agentId,
        string teeArch,
        bytes32 codeMeasurement
    );

    function registerTEEKey(
        uint256 agentId,
        string calldata teeArch,
        bytes32 codeMeasurement,
        bytes calldata pubkey,
        bytes calldata proof
    ) external returns (uint256 keyId);

    function verifyTEEKey(uint256 keyId) external view returns (bool);
    function getTEEKey(uint256 keyId) external view returns (TEEKey memory);
}
