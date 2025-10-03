// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "./IAutomataDcapAttestation.sol";

import "forge-std/console.sol";

contract DstackOffchainVerifier {

    address public validatorPublicKey;
    address public dcapVerifier;

    bytes referenceMrTd;
    bytes referenceMrConfigId;
    bytes referenceRtMr0;
    bytes referenceRtMr1;
    bytes referenceRtMr2;
    bytes referenceRtMr3;

    constructor(address _dcapVerifier) {
        dcapVerifier = _dcapVerifier;
    }

    function setReferenceValues(
        bytes calldata _referenceMrTd,
        bytes calldata _referenceMrConfigId,
        bytes calldata _referenceRtMr0,
        bytes calldata _referenceRtMr1,
        bytes calldata _referenceRtMr2,
        bytes calldata _referenceRtMr3
    ) external {
        referenceMrTd = _referenceMrTd;
        referenceMrConfigId = _referenceMrConfigId;
        referenceRtMr0 = _referenceRtMr0;
        referenceRtMr1 = _referenceRtMr1;
        referenceRtMr2 = _referenceRtMr2;
        referenceRtMr3 = _referenceRtMr3;
    }

    function initValidator(address _validatorPublicKey, bytes calldata rawQuote) external {
        // Verify DCAP attestation first
        // TODO: Uncomment this when the DCAP attestation is implemented
        (bool success, bytes memory output) = IAutomataDcapAttestation(dcapVerifier).verifyAndAttestOnChain(rawQuote);
        require(success, "DCAP verification failed");

        // Extract and verify public key
        bytes memory reportData = substring(rawQuote, 520+48, 64);        

        address publicKey = address(uint160(uint256(bytes32(reportData)) >> 96));
        console.logAddress(publicKey);
        require(publicKey == _validatorPublicKey, "Invalid public key");

        // Verify measurements
        _verifyMeasurements(rawQuote);
        validatorPublicKey = publicKey;
    }

    function _verifyMeasurements(bytes memory reportBytes) internal view {

        // console.log all the values
        {
            console.logBytes(substring(reportBytes, 136+48, 48));
            console.logBytes(substring(reportBytes, 184+48, 48));
            console.logBytes(substring(reportBytes, 328+48, 48));
            console.logBytes(substring(reportBytes, 376+48, 48));
            console.logBytes(substring(reportBytes, 424+48, 48));
            console.logBytes(substring(reportBytes, 472+48, 48));
        }

        require(keccak256(substring(reportBytes, 136+48, 48)) == keccak256(referenceMrTd), "Invalid mrTd");
        require(keccak256(substring(reportBytes, 184+48, 48)) == keccak256(referenceMrConfigId), "Invalid mrConfigId");
        require(keccak256(substring(reportBytes, 328+48, 48)) == keccak256(referenceRtMr0), "Invalid rtMr0");
        require(keccak256(substring(reportBytes, 376+48, 48)) == keccak256(referenceRtMr1), "Invalid rtMr1");
        require(keccak256(substring(reportBytes, 424+48, 48)) == keccak256(referenceRtMr2), "Invalid rtMr2");
        require(keccak256(substring(reportBytes, 472+48, 48)) == keccak256(referenceRtMr3), "Invalid rtMr3");
    }

    // Verify the offchain compressed proof
    //
    // The real validation happened offchain by the validator. Validator acts as an oracle to
    // provide the proof for onchain verification
    function verify(
        bytes32 codeMeasurement,
        address pubkey,
        string calldata codeConfigUri,
        bytes calldata proof
    ) external view returns (bool) {
        // Verify the signature from the validator
        (bytes32 message, bytes memory signature) = abi.decode(proof, (bytes32, bytes));
        require(ECDSA.recover(message, signature) == validatorPublicKey, "Invalid signature");

        // Verify the claims
        (bytes32 expectedMeasurement, address expectedPubkey, string memory expectedCodeConfigUri) = abi.decode(abi.encodePacked(message), (bytes32, address, string));
        return (
            expectedMeasurement == codeMeasurement
            && expectedPubkey == pubkey
            && keccak256(bytes(expectedCodeConfigUri)) == keccak256(bytes(codeConfigUri))
        );
    }

    function substring(bytes memory data, uint256 start, uint256 length) internal pure returns (bytes memory) {
        bytes memory result = new bytes(length);
        for (uint256 i = 0; i < length; i++) {
            result[i] = data[start + i];
        }
        return result;
    }

}
