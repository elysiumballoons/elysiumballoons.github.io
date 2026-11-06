require("@nomicfoundation/hardhat-ethers");
require("dotenv").config();

const accounts = process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [];

module.exports = {
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 200 }, evmVersion: "cancun" },
  },
  networks: {
    // Elysium mainnet (opens 9 Nov 2026). Chain ID 99901.
    // Put the OFFICIAL public RPC from Kinetiq in .env as ELYSIUM_RPC once it is published.
    elysium: {
      url: process.env.ELYSIUM_RPC || "https://REPLACE-WITH-OFFICIAL-ELYSIUM-RPC",
      chainId: 99901,
      accounts,
    },
    // Elysium testnet (live). Chain ID 99801. Faucet: https://elysium.kinetiq.xyz/testnet-faucet
    elysiumTestnet: {
      url: process.env.ELYSIUM_TESTNET_RPC || "https://testnet-rpc.elysium.kinetiq.xyz",
      chainId: 99801,
      accounts,
    },
  },
};
