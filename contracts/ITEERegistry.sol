// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ITEERegistry {
    struct Verifier {
        bytes32 teeArch;
        // ... more verifier metadata
    }

    struct Key {
        bytes32 teeArch;
        bytes32 codeMeasurement;
        bytes pubkey;
        string codeConfigUri;
        address verifier;
    }

    event VerifierAdded(address indexed verifier, bytes32 vendor);
    event VerifierRemoved(address indexed verifier);
    event KeyAdded(
        uint256 indexed agentId,
        bytes32 teeArch,
        bytes32 codeMeasurement,
        address pubkey,
        string codeConfigUri,
        address verifier
    );

    event KeyRemoved(
        uint256 indexed agentId,
        address pubkey
    );

    function verifiers(address verifier) external view returns (Verifier memory);
    function keys(uint256 agentId, address pubkey) external view returns (Key memory);

    function addVerifier(address verifier, bytes32 vendor) external;
    function removeVerifier(address verifier) external;
    
    function addKey(
        uint256 agentId,
        bytes32 teeArch,
        bytes32 codeMeasurement,
        address pubkey,
        string calldata codeConfigUri,
        address verifier,
        bytes calldata proof
    ) external;
    
    function removeKey(
        uint256 agentId,
        address pubkey
    ) external;
    
    function getKey(uint256 agentId, address pubkey) external view returns (Key memory);
    function hasKey(uint256 agentId, address pubkey) external view returns (bool);
    function getKeyCount(uint256 agentId) external view returns (uint256);
    function getKeyAtIndex(uint256 agentId, uint256 index) external view returns (address);
    function isVerifier(address verifier) external view returns (bool);
}
