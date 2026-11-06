// Usage: npm run set-base-url -- https://your-site.vercel.app
// Rewrites every public/nft/metadata/N.json "image" to <site>/nft/images/N.png
// and writes public/nft/metadata/collection.json (used by contractURI()).
import fs from "node:fs";
import path from "node:path";

const site = (process.argv[2] || "").replace(/\/+$/, "");
if (!/^https?:\/\//.test(site)) {
  console.error("Give your site URL, e.g. npm run set-base-url -- https://elysiumballons.vercel.app");
  process.exit(1);
}
const dir = path.resolve("public/nft/metadata");
let n = 0;
for (const f of fs.readdirSync(dir)) {
  if (!/^\d+\.json$/.test(f)) continue;
  const p = path.join(dir, f);
  const m = JSON.parse(fs.readFileSync(p, "utf8"));
  m.image = `${site}/nft/images/${f.replace(".json", ".png")}`;
  fs.writeFileSync(p, JSON.stringify(m));
  n++;
}
fs.writeFileSync(
  path.join(dir, "collection.json"),
  JSON.stringify(
    {
      name: "Elysium Balloons",
      description: "10,000 happy pixel balloons floating over the Elysian sky. On Elysium, the HYPE L2.",
      image: `${site}/nft/images/1.png`,
      external_link: site,
      seller_fee_basis_points: 1000,
    },
    null,
    1
  )
);
console.log(`Updated ${n} metadata files. Contract BASE_URI = ${site}/nft/metadata/`);
