const { ethers } = require('hardhat');

async function main() {
  const IdentityRegistry = await ethers.getContractFactory('IdentityRegistry');
  const registry = await IdentityRegistry.deploy();
  await registry.deployed();

  console.log('IdentityRegistry deployed to:', registry.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
