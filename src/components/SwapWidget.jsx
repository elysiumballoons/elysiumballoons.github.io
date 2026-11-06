import { LiFiWidget } from "@lifi/widget";

// Swap any token on any chain into native HYPE on HyperEVM (chain 999).
// When LI.FI lists Elysium (99901), set toChain to 99901 to swap straight into Elysium.
const config = {
  integrator: "elysium-balloons",
  appearance: "light",
  variant: "compact",
  toChain: 999,
  toToken: "0x0000000000000000000000000000000000000000",
  hiddenUI: ["poweredBy", "appearance", "language"],
  theme: {
    container: { border: "none", borderRadius: "12px", boxShadow: "none", maxWidth: "100%" },
    palette: {
      primary: { main: "#e8394a" },
      secondary: { main: "#5ef2c9" },
      background: { default: "#ffffff", paper: "#f4fbff" },
      text: { primary: "#1b1530" },
    },
    shape: { borderRadius: 12, borderRadiusSecondary: 12 },
    typography: { fontFamily: "Figtree, system-ui, sans-serif" },
  },
};

export default function SwapWidget() {
  return <LiFiWidget integrator="elysium-balloons" config={config} />;
}
