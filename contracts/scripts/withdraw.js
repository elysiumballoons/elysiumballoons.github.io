// Usage: npm run withdraw   -> sends all mint HYPE from the contract to TO (default: the deployer wallet)
const hre = require("hardhat");
const ADDRESS = process.env.CONTRACT_ADDRESS || "0xA1df38bEbd8da5ae5014899b283BADA100868569";

async function main() {
  const [me] = await hre.ethers.getSigners();
  const to = process.env.TO || me.address;
  const c = await hre.ethers.getContractAt("ElysiumBalloons", ADDRESS);
  const bal = await hre.ethers.provider.getBalance(ADDRESS);
  console.log("In contract:", hre.ethers.formatEther(bal), "HYPE");
  if (bal === 0n) return console.log("Nothing to withdraw.");
  const tx = await c.withdraw(to);
  await tx.wait();
  console.log("Sent to", to, "tx:", tx.hash);
}
main().catch((e) => { console.error(e.shortMessage || e.message); process.exit(1); });
