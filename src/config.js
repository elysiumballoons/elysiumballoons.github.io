import { defineChain } from "viem";

// ---------------------------------------------------------------------------
//  Everything you need to edit lives here (or in a .env file, see .env.example)
// ---------------------------------------------------------------------------

// "mainnet" (default) or "testnet"
export const NETWORK = import.meta.env.VITE_NETWORK === "testnet" ? "testnet" : "mainnet";

// Paste the address printed by `npm run deploy:mainnet` (contracts folder)
const DEPLOYED = "0xADRESSE_JDIDA";
const envAddr = (import.meta.env.VITE_CONTRACT_ADDRESS || "").trim();
// Only use the env value if it is a real address; otherwise fall back to the deployed mainnet contract.
export const CONTRACT_ADDRESS = /^0x[0-9a-fA-F]{40}$/.test(envAddr) ? envAddr : DEPLOYED;

// Bridge HyperEVM -> Elysium (official Kinetiq app). Override with VITE_BRIDGE_URL if Kinetiq gives a direct bridge page.
export const BRIDGE_URL = import.meta.env.VITE_BRIDGE_URL || "https://elysium.kinetiq.xyz";

export const X_URL = import.meta.env.VITE_X_URL || "https://x.com/";
export const COLLECTION_SIZE = 10000;

export const elysium = defineChain({
  id: 99901,
  name: "Elysium",
  nativeCurrency: { name: "HYPE", symbol: "HYPE", decimals: 18 },
  // Official public RPC from Kinetiq docs. For heavy traffic use Alchemy: https://elysium-mainnet.g.alchemy.com/v2/KEY
  rpcUrls: { default: { http: [/^https:\/\//.test(import.meta.env.VITE_ELYSIUM_RPC || "") && !/elysp\.com/.test(import.meta.env.VITE_ELYSIUM_RPC) ? import.meta.env.VITE_ELYSIUM_RPC : "https://rpc.elysium.kinetiq.xyz"] } },
  blockExplorers: { default: { name: "Elysium Explorer", url: "https://elysium.kinetiq.xyz/explorer" } },
});

export const elysiumTestnet = defineChain({
  id: 99801,
  name: "Elysium Testnet",
  nativeCurrency: { name: "HYPE", symbol: "HYPE", decimals: 18 },
  rpcUrls: { default: { http: [import.meta.env.VITE_ELYSIUM_TESTNET_RPC || "https://testnet-rpc.elysium.kinetiq.xyz"] } },
  blockExplorers: { default: { name: "Elysium Testnet Explorer", url: "https://elysium.kinetiq.xyz/testnet-explorer" } },
  testnet: true,
});

export const hyperEvm = defineChain({
  id: 999,
  name: "HyperEVM",
  nativeCurrency: { name: "HYPE", symbol: "HYPE", decimals: 18 },
  rpcUrls: { default: { http: ["https://rpc.hyperliquid.xyz/evm"] } },
  blockExplorers: { default: { name: "HyperEVMScan", url: "https://hyperevmscan.io" } },
});

export const TARGET_CHAIN = NETWORK === "testnet" ? elysiumTestnet : elysium;

export const ABI = [
  { type: "function", name: "mint", stateMutability: "payable", inputs: [{ name: "quantity", type: "uint256" }], outputs: [] },
  { type: "function", name: "price", stateMutability: "view", inputs: [], outputs: [{ type: "uint256" }] },
  { type: "function", name: "totalSupply", stateMutability: "view", inputs: [], outputs: [{ type: "uint256" }] },
  { type: "function", name: "maxPerWallet", stateMutability: "view", inputs: [], outputs: [{ type: "uint256" }] },
  { type: "function", name: "mintOpen", stateMutability: "view", inputs: [], outputs: [{ type: "bool" }] },
  { type: "function", name: "mintedBy", stateMutability: "view", inputs: [{ type: "address" }], outputs: [{ type: "uint256" }] },
  { type: "event", name: "Minted", inputs: [
    { name: "to", type: "address", indexed: true },
    { name: "firstId", type: "uint256", indexed: false },
    { name: "quantity", type: "uint256", indexed: false },
  ] },
];
