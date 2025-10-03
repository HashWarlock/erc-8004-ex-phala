//SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

enum ZkCoProcessorType {
    // if the ZkCoProcessorType is included as None in the AttestationSubmitted event log
    // it indicates that the attestation of the DCAP quote is executed entirely on-chain
    None,
    RiscZero,
    Succinct
}

interface IAutomataDcapAttestationFee {
    function verifyAndAttestOnChain(bytes calldata rawQuote)
        external
        payable
        returns (bool success, bytes memory output);

    function verifyAndAttestWithZKProof(
        bytes calldata output,
        ZkCoProcessorType zkCoprocessor,
        bytes calldata proofBytes
    ) external payable returns (bool success, bytes memory verifiedOutput);
}