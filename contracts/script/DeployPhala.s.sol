// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Script.sol";
import "../src/IdentityRegistry.sol";
import "../src/ReputationRegistry.sol";
import "../src/ValidationRegistry.sol";

contract DeployPhala is Script {
    // Phala testnet specific configuration
    uint256 constant PHALA_CHAIN_ID = 1001;
    
    function run() external {
        // Get deployer private key
        uint256 deployerPrivateKey = vm.envUint("DEPLOYER_KEY");
        address deployer = vm.addr(deployerPrivateKey);
        
        console.log("Deploying to Phala Cloud with deployer:", deployer);
        console.log("Chain ID:", block.chainid);
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy IdentityRegistry
        IdentityRegistry identityRegistry = new IdentityRegistry();
        console.log("IdentityRegistry deployed at:", address(identityRegistry));
        
        // Deploy ReputationRegistry with IdentityRegistry address
        ReputationRegistry reputationRegistry = new ReputationRegistry(address(identityRegistry));
        console.log("ReputationRegistry deployed at:", address(reputationRegistry));
        
        // Deploy ValidationRegistry with IdentityRegistry address
        ValidationRegistry validationRegistry = new ValidationRegistry(address(identityRegistry));
        console.log("ValidationRegistry deployed at:", address(validationRegistry));
        
        vm.stopBroadcast();
        
        // Verify deployment
        console.log("\n=== Deployment Summary ===");
        console.log("Network: Phala Cloud Testnet");
        console.log("Chain ID:", block.chainid);
        console.log("Deployer:", deployer);
        console.log("\nContract Addresses:");
        console.log("IdentityRegistry:  ", address(identityRegistry));
        console.log("ReputationRegistry:", address(reputationRegistry));
        console.log("ValidationRegistry:", address(validationRegistry));
        
        // Save deployment info to file for verification
        string memory deploymentInfo = string(abi.encodePacked(
            "PHALA_DEPLOYMENT\n",
            "IdentityRegistry=", vm.toString(address(identityRegistry)), "\n",
            "ReputationRegistry=", vm.toString(address(reputationRegistry)), "\n",
            "ValidationRegistry=", vm.toString(address(validationRegistry)), "\n"
        ));
        
        vm.writeFile("./phala-deployment.txt", deploymentInfo);
        console.log("\nDeployment info saved to phala-deployment.txt");
    }
}