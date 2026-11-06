import { lazy, Suspense, useState } from "react";
import { BRIDGE_URL, hyperEvm, TARGET_CHAIN } from "../config";

const SwapWidget = lazy(() => import("./SwapWidget"));

export default function GetHype() {
  const [tab, setTab] = useState("swap");
  return (
    <section className="section" id="hype">
      <div className="hype-copy">
        <h2>Need HYPE on Elysium?</h2>
        <p>
          Minting is paid in HYPE on {TARGET_CHAIN.name}. Swap any token into HYPE on HyperEVM, then bridge it across.
          Two steps, both from this page.
        </p>
        <ol className="steps">
          <li><strong>Swap</strong> ETH, USDC or anything else into HYPE on HyperEVM.</li>
          <li><strong>Bridge</strong> that HYPE from HyperEVM to Elysium.</li>
          <li><strong>Mint</strong> your balloons.</li>
        </ol>
      </div>

      <div className="hype-panel pixel-box">
        <div className="tabs" role="tablist">
          <button role="tab" aria-selected={tab === "swap"} className={tab === "swap" ? "on" : ""} onClick={() => setTab("swap")}>Swap</button>
          <button role="tab" aria-selected={tab === "bridge"} className={tab === "bridge" ? "on" : ""} onClick={() => setTab("bridge")}>Bridge</button>
        </div>
        {tab === "swap" ? (
          <Suspense fallback={<div className="widget-loading">Loading swap…</div>}>
            <SwapWidget />
          </Suspense>
        ) : (
          <div className="bridge">
            <div className="route">
              <span className="node">{hyperEvm.name}</span>
              <span className="route-line" aria-hidden="true" />
              <span className="node node-hot">{TARGET_CHAIN.name}</span>
            </div>
            <p>HYPE bridges 1:1 from HyperEVM to Elysium. Deposits arrive in a few minutes; withdrawals back to HyperEVM wait for a challenge period.</p>
            <a className="btn btn-red btn-lg" href={BRIDGE_URL} target="_blank" rel="noreferrer">Open the bridge</a>
            <p className="fine">Always check you are on the official Kinetiq bridge before signing.</p>
          </div>
        )}
      </div>
    </section>
  );
}
