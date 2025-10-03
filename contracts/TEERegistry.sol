// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "./ITEERegistry.sol";

contract TEERegistry is ITEERegistry {
    mapping(uint256 => TEEKey) public teeKeys;
    mapping(address => bool) public whitelistedVerifiers;
    uint256 public nextKeyId = 1;

    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function whitelistVerifier(address verifier, bool status) external onlyOwner {
        whitelistedVerifiers[verifier] = status;
    }

    function registerTEEKey(
        uint256 agentId,
        string calldata teeArch,
        bytes32 codeMeasurement,
        bytes calldata pubkey,
        bytes calldata proof
    ) external override returns (uint256) {
        require(whitelistedVerifiers[msg.sender], "Verifier not whitelisted");

        uint256 keyId = nextKeyId++;

        teeKeys[keyId] = TEEKey({
            agentId: agentId,
            teeArch: teeArch,
            codeMeasurement: codeMeasurement,
            pubkey: pubkey,
            verifier: msg.sender,
            timestamp: block.timestamp
        });

        emit TEEKeyRegistered(keyId, agentId, teeArch, codeMeasurement);

        return keyId;
    }

    function verifyTEEKey(uint256 keyId) external view override returns (bool) {
        return teeKeys[keyId].timestamp > 0;
    }

    function getTEEKey(uint256 keyId) external view override returns (TEEKey memory) {
        return teeKeys[keyId];
    }
}
