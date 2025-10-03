// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IAutomataDcapAttestation {
    function verifyAndAttestOnChain(bytes calldata rawQuote) external returns (bool, bytes memory);
}
