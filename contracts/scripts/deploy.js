const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const baseURI = process.env.BASE_URI;            // e.g. https://your-site.vercel.app/nft/metadata/
  const royalty = process.env.ROYALTY_RECEIVER || deployer.address;
  if (!baseURI) throw new Error("Set BASE_URI in contracts/.env (must end with /)");

  console.log("Deployer:", deployer.address);
  console.log("Balance :", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "HYPE");

  const C = await hre.ethers.getContractFactory("ElysiumBalloons");
  const c = await C.deploy(baseURI, royalty);
  await c.waitForDeployment();
  const addr = await c.getAddress();
  console.log("ElysiumBalloons deployed at:", addr);
  console.log("\nNext:\n 1) put this address in site config (src/config.js -> CONTRACT_ADDRESS)\n 2) open the mint: npx hardhat console --network", hre.network.name,
    `\n    > const c = await ethers.getContractAt("ElysiumBalloons","${addr}"); await c.setMintOpen(true)`);
}

main().catch((e) => { console.error(e); process.exit(1); });
