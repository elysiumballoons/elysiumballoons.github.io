// Usage: npm run open-mint     (or: npm run close-mint)
const hre = require("hardhat");
const ADDRESS = process.env.CONTRACT_ADDRESS || "0xA1df38bEbd8da5ae5014899b283BADA100868569";

async function main() {
  const open = process.env.MINT_OPEN !== "false";
  const c = await hre.ethers.getContractAt("ElysiumBalloons", ADDRESS);
  console.log("Contract:", ADDRESS);
  console.log("Mint open before:", await c.mintOpen());
  const tx = await c.setMintOpen(open);
  console.log("Tx sent:", tx.hash);
  await tx.wait();
  console.log("Mint open now   :", await c.mintOpen());
  console.log("Price           :", hre.ethers.formatEther(await c.price()), "HYPE");
  console.log("Minted          :", (await c.totalSupply()).toString(), "/ 10000");
}
main().catch((e) => { console.error(e.shortMessage || e.message); process.exit(1); });
