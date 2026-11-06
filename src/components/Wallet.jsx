import { useState } from "react";
import { useAccount, useConnect, useDisconnect, useBalance, useSwitchChain } from "wagmi";
import { TARGET_CHAIN } from "../config";

export const short = (a) => (a ? `${a.slice(0, 6)}…${a.slice(-4)}` : "");

export function WalletButton() {
  const { address, isConnected, chainId } = useAccount();
  const { disconnect } = useDisconnect();
  const { switchChain } = useSwitchChain();
  const [open, setOpen] = useState(false);
  const { data: bal } = useBalance({ address, chainId: TARGET_CHAIN.id, query: { enabled: !!address } });

  if (!isConnected) {
    return (
      <>
        <button className="btn btn-ink" onClick={() => setOpen(true)}>Connect wallet</button>
        {open && <ConnectModal onClose={() => setOpen(false)} />}
      </>
    );
  }
  const wrong = chainId !== TARGET_CHAIN.id;
  return (
    <div className="wallet-chip">
      {wrong ? (
        <button className="btn btn-red btn-sm" onClick={() => switchChain({ chainId: TARGET_CHAIN.id })}>
          Switch to {TARGET_CHAIN.name}
        </button>
      ) : (
        <span className="wallet-bal">{bal ? `${Number(bal.formatted).toFixed(3)} HYPE` : "…"}</span>
      )}
      <button className="btn btn-paper btn-sm" onClick={() => disconnect()} title="Disconnect">
        {short(address)}
      </button>
    </div>
  );
}

export function ConnectModal({ onClose }) {
  const { connectors, connect, isPending, error } = useConnect();
  // Prefer discovered wallets (EIP-6963); hide the generic "Injected" entry when real ones exist.
  const named = connectors.filter((c) => c.id !== "injected");
  const list = named.length ? named : connectors;
  return (
    <div className="modal-back" onClick={onClose}>
      <div className="modal pixel-box" role="dialog" aria-label="Connect a wallet" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>Connect a wallet</h3>
          <button className="icon-btn" onClick={onClose} aria-label="Close">✕</button>
        </div>
        <div className="wallet-list">
          {list.map((c) => (
            <button
              key={c.uid}
              className="wallet-opt"
              disabled={isPending}
              onClick={() => connect({ connector: c, chainId: TARGET_CHAIN.id }, { onSuccess: onClose })}
            >
              {c.icon ? <img src={c.icon} alt="" /> : <span className="wallet-dot" />}
              <span>{c.id === "injected" ? "Browser wallet" : c.name}</span>
            </button>
          ))}
        </div>
        {error && <p className="err">{error.shortMessage || error.message}</p>}
        <p className="fine">No wallet? Install Rabby or MetaMask, then refresh this page.</p>
      </div>
    </div>
  );
}
