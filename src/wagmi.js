import { createConfig, http } from "wagmi";
import { mainnet, arbitrum, base, bsc, optimism } from "viem/chains";
import { injected, walletConnect } from "wagmi/connectors";
import { TARGET_CHAIN, hyperEvm } from "./config";

const wcId = import.meta.env.VITE_WC_PROJECT_ID;

// Elysium for minting + the usual chains so the swap panel can pull funds from anywhere.
const chains = [TARGET_CHAIN, hyperEvm, mainnet, arbitrum, base, optimism, bsc];

export const wagmiConfig = createConfig({
  chains,
  connectors: [
    injected({ shimDisconnect: true }),
    ...(wcId ? [walletConnect({ projectId: wcId, showQrModal: true })] : []),
  ],
  multiInjectedProviderDiscovery: true, // lists MetaMask, Rabby, OKX, Phantom… automatically
  transports: Object.fromEntries(chains.map((c) => [c.id, http()])),
});
