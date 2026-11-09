# Elysium Balloons 🎈

10,000 pixel-art balloons with faces, floating in the sky — minted on **Elysium** (Kinetiq's HYPE L2, chain `99901`).

- **Art**: `public/nft/images/1..10000.png` (480×480 pixel art) + `public/nft/metadata/1..10000.json`, 12 trait groups, 5 one-of-one legendaries, every balloon unique.
- **Contract**: `contracts/contracts/ElysiumBalloons.sol` — ERC-721, 0.01 HYPE, max 100 per wallet, 10% royalties (ERC-2981), owner can pause/open, change price, set base URI, withdraw.
- **Site**: Vite + React + wagmi. Animated sky, wallet connect (MetaMask, Rabby, OKX… auto-detected), mint with quantity, network switch to Elysium, swap any token into HYPE (LI.FI), bridge link, gallery with trait lookup, rarity table.

## 1. Deploy the site (Vercel or Netlify)
Import this repo. Build command `npm run build`, output folder `dist`.
Set these environment variables in the host:

| Variable | Value |
|---|---|
| `VITE_ELYSIUM_RPC` | optional, defaults to the official `https://rpc.elysium.kinetiq.xyz` |
| `VITE_CONTRACT_ADDRESS` | your contract address (step 3) |
| `VITE_BRIDGE_URL` | bridge link (defaults to the official https://elysium.kinetiq.xyz) |
| `VITE_X_URL` | your X account |
| `VITE_WC_PROJECT_ID` | optional, WalletConnect project id for mobile QR |
| `VITE_NETWORK` | `testnet` to test on Elysium testnet (99801) |

## 2. Point metadata to your domain
```bash
npm install
npm run set-base-url -- https://YOUR-SITE.vercel.app
git commit -am "metadata urls" && git push
```

## 3. Deploy the contract
```bash
cd contracts
npm install
cp .env.example .env      # fill PRIVATE_KEY, ELYSIUM_RPC, BASE_URI=https://YOUR-SITE.vercel.app/nft/metadata/
npm run deploy:testnet    # try on testnet first (faucet: elysium.kinetiq.xyz/testnet-faucet)
npm run deploy:mainnet
```
Then open the mint (`setMintOpen(true)`) and put the address in `VITE_CONTRACT_ADDRESS`.

## Regenerate the art
```bash
python3 art/generate.py          # deterministic (fixed seed), same 10,000 every time
python3 art/floaters.py          # transparent balloons for the hero animation
```
