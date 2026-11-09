// Usage: set BASE_URI in contracts/.env (must end with /nft/metadata/), then: npm run set-base-uri
const hre = require("hardhat");
const ADDRESS = process.env.CONTRACT_ADDRESS || "0xA1df38bEbd8da5ae5014899b283BADA100868569";

async function main() {
  const uri = process.env.BASE_URI;
  if (!uri || !uri.endsWith("/")) throw new Error("Set BASE_URI in .env, ending with / (e.g. https://xxx.vercel.app/nft/metadata/)");
  const c = await hre.ethers.getContractAt("ElysiumBalloons", ADDRESS);
  const tx = await c.setBaseURI(uri);
  console.log("Tx sent:", tx.hash);
  await tx.wait();
  console.log("Base URI is now:", uri);
  console.log("Collection metadata:", await c.contractURI());
}
main().catch((e) => { console.error(e.shortMessage || e.message); process.exit(1); });
