// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./ITEERegistry.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract TEERegistry is ITEERegistry, Ownable {
    using EnumerableSet for EnumerableSet.AddressSet;

    address public identityRegistry;

    mapping(address => Verifier) private _verifiers;
    mapping(uint256 => EnumerableSet.AddressSet) private _agentKeys;
    mapping(address => Key) private _keys;

    constructor(address _identityRegistry) Ownable(msg.sender) {
        identityRegistry = _identityRegistry;
    }

    function verifiers(address verifier) external view returns (Verifier memory) {
        return _verifiers[verifier];
    }

    function keys(uint256 agentId, address pubkey) external view returns (Key memory) {
        return _keys[pubkey];
    }

    function addVerifier(address verifier, bytes32 teeArch) external onlyOwner {
        require(verifier != address(0), "Invalid verifier address");

        _verifiers[verifier] = Verifier({
            teeArch: teeArch
        });

        emit VerifierAdded(verifier, teeArch);
    }

    function removeVerifier(address verifier) external onlyOwner {
        require(verifier != address(0), "Invalid verifier address");

        delete _verifiers[verifier];

        emit VerifierRemoved(verifier);
    }

    function addKey(
        uint256 agentId,
        bytes32 teeArch,
        bytes32 codeMeasurement,
        address pubkey,
        string calldata codeConfigUri,
        address verifier,
        bytes calldata proof
    ) external {
        // TODO: Verify caller is owner/operator of agentId via identityRegistry

        // TODO: Verify that verifier is whitelisted
        require(_verifiers[verifier].teeArch != bytes32(0), "Verifier not whitelisted");

        // Verify key doesn't already exist
        require(_keys[pubkey].verifier == address(0), "Key already exists");

        // TODO: Call verifier to validate proof
        // The verifier should validate:
        // - The TEE attestation is valid
        // - The codeMeasurement matches the public input in the proof
        // - The pubkey matches the public input in the proof

        _keys[pubkey] = Key({
            teeArch: teeArch,
            codeMeasurement: codeMeasurement,
            pubkey: abi.encodePacked(pubkey),
            codeConfigUri: codeConfigUri,
            verifier: verifier
        });

        _agentKeys[agentId].add(pubkey);

        emit KeyAdded(agentId, teeArch, codeMeasurement, pubkey, codeConfigUri, verifier);
    }

    function removeKey(
        uint256 agentId,
        address pubkey
    ) external {
        // TODO: Verify caller is owner/operator of agentId via identityRegistry

        require(_agentKeys[agentId].contains(pubkey), "Key not found");

        _agentKeys[agentId].remove(pubkey);
        delete _keys[pubkey];

        emit KeyRemoved(agentId, pubkey);
    }

    function getKey(uint256 agentId, address pubkey) external view returns (Key memory) {
        require(_agentKeys[agentId].contains(pubkey), "Key not found");
        return _keys[pubkey];
    }

    function hasKey(uint256 agentId, address pubkey) external view returns (bool) {
        return _agentKeys[agentId].contains(pubkey);
    }

    function getKeyCount(uint256 agentId) external view returns (uint256) {
        return _agentKeys[agentId].length();
    }

    function getKeyAtIndex(uint256 agentId, uint256 index) external view returns (address) {
        return _agentKeys[agentId].at(index);
    }

    function isVerifier(address verifier) external view returns (bool) {
        return _verifiers[verifier].teeArch != bytes32(0);
    }

    function getIdentityRegistry() external view returns (address) {
        return identityRegistry;
    }
}
