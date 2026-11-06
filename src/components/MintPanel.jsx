import { useEffect, useMemo, useState } from "react";
import { formatEther, parseEventLogs } from "viem";
import {
  useAccount, useReadContracts, useWriteContract, useWaitForTransactionReceipt, useSwitchChain, useBalance,
} from "wagmi";
import { ABI, CONTRACT_ADDRESS, TARGET_CHAIN, COLLECTION_SIZE } from "../config";
import { ConnectModal } from "./Wallet";

const live = /^0x[0-9a-fA-F]{40}$/.test(CONTRACT_ADDRESS);

export default function MintPanel() {
  const { address, isConnected, chainId } = useAccount();
  const { switchChain, isPending: switching } = useSwitchChain();
  const [qty, setQty] = useState(1);
  const [connectOpen, setConnectOpen] = useState(false);
  const c = { address: CONTRACT_ADDRESS, abi: ABI, chainId: TARGET_CHAIN.id };

  const { data, refetch } = useReadContracts({
    contracts: [
      { ...c, functionName: "totalSupply" },
      { ...c, functionName: "price" },
      { ...c, functionName: "maxPerWallet" },
      { ...c, functionName: "mintOpen" },
      { ...c, functionName: "mintedBy", args: [address ?? "0x0000000000000000000000000000000000000000"] },
    ],
    query: { enabled: live, refetchInterval: 8000 },
  });
  const { data: bal } = useBalance({ address, chainId: TARGET_CHAIN.id, query: { enabled: !!address } });

  const minted = Number(data?.[0]?.result ?? 0n);
  const price = data?.[1]?.result ?? 10000000000000000n; // 0.01 HYPE
  const maxPer = Number(data?.[2]?.result ?? 100n);
  const open = Boolean(data?.[3]?.result);
  const mine = Number(data?.[4]?.result ?? 0n);
  const left = Math.max(0, Math.min(maxPer - mine, COLLECTION_SIZE - minted));
  const total = price * BigInt(qty);

  useEffect(() => { if (qty > Math.max(1, left)) setQty(Math.max(1, left)); }, [left]); // eslint-disable-line

  const { writeContract, data: hash, isPending, error: wErr, reset } = useWriteContract();
  const { data: receipt, isLoading: confirming, isSuccess } = useWaitForTransactionReceipt({ hash, chainId: TARGET_CHAIN.id });

  const newIds = useMemo(() => {
    if (!receipt) return [];
    const ev = parseEventLogs({ abi: ABI, logs: receipt.logs, eventName: "Minted" })[0];
    if (!ev) return [];
    const first = Number(ev.args.firstId);
    return Array.from({ length: Number(ev.args.quantity) }, (_, i) => first + i);
  }, [receipt]);

  useEffect(() => { if (isSuccess) refetch(); }, [isSuccess, refetch]);

  const pct = (minted / COLLECTION_SIZE) * 100;
  const wrongChain = isConnected && chainId !== TARGET_CHAIN.id;
  const lowBal = bal && bal.value < total;

  let action;
  if (!live) action = <button className="btn btn-red btn-lg" disabled>Mint opens soon</button>;
  else if (!isConnected) action = <button className="btn btn-red btn-lg" onClick={() => setConnectOpen(true)}>Connect wallet to mint</button>;
  else if (wrongChain) action = (
    <button className="btn btn-red btn-lg" disabled={switching} onClick={() => switchChain({ chainId: TARGET_CHAIN.id })}>
      {switching ? "Check your wallet…" : `Switch to ${TARGET_CHAIN.name}`}
    </button>
  );
  else if (!open) action = <button className="btn btn-red btn-lg" disabled>Mint is paused</button>;
  else if (minted >= COLLECTION_SIZE) action = <button className="btn btn-red btn-lg" disabled>Sold out</button>;
  else if (left === 0) action = <button className="btn btn-red btn-lg" disabled>Wallet limit reached</button>;
  else action = (
    <button
      className="btn btn-red btn-lg"
      disabled={isPending || confirming}
      onClick={() => { reset(); writeContract({ ...c, functionName: "mint", args: [BigInt(qty)], value: total }); }}
    >
      {isPending ? "Confirm in wallet…" : confirming ? "Inflating…" : `Mint ${qty} balloon${qty > 1 ? "s" : ""}`}
    </button>
  );

  return (
    <div className="mint pixel-box" id="mint">
      <div className="mint-row">
        <span>Minted</span>
        <strong>{live ? minted.toLocaleString() : "0"} / {COLLECTION_SIZE.toLocaleString()}</strong>
      </div>
      <div className="bar" role="progressbar" aria-valuenow={minted} aria-valuemin={0} aria-valuemax={COLLECTION_SIZE}>
        <div className="bar-fill" style={{ width: `${Math.max(pct, 0.6)}%` }} />
      </div>

      <div className="qty">
        <button className="qty-btn" aria-label="One less" onClick={() => setQty((q) => Math.max(1, q - 1))}>−</button>
        <input
          aria-label="How many balloons"
          inputMode="numeric"
          value={qty}
          onChange={(e) => {
            const n = parseInt(e.target.value.replace(/\D/g, "") || "1", 10);
            setQty(Math.min(Math.max(1, n), Math.max(1, left || maxPer)));
          }}
        />
        <button className="qty-btn" aria-label="One more" onClick={() => setQty((q) => Math.min(Math.max(1, left || maxPer), q + 1))}>+</button>
        <div className="quick">
          {[5, 10, 25].map((n) => (
            <button key={n} className="chip" onClick={() => setQty(Math.min(n, Math.max(1, left || maxPer)))}>{n}</button>
          ))}
          <button className="chip" onClick={() => setQty(Math.max(1, left || maxPer))}>Max</button>
        </div>
      </div>

      <div className="mint-row total">
        <span>Total</span>
        <strong>{formatEther(total)} HYPE</strong>
      </div>
      <p className="fine">{formatEther(price)} HYPE each · up to {maxPer} per wallet{isConnected && live ? ` · you minted ${mine}` : ""}</p>

      {action}

      {lowBal && isConnected && !wrongChain && open && (
        <p className="warn">You need {formatEther(total)} HYPE on Elysium plus a little for gas. <a href="#hype">Get HYPE</a></p>
      )}
      {wErr && <p className="err">{wErr.shortMessage || wErr.message}</p>}
      {hash && (
        <p className="fine">
          Transaction: <a href={`${TARGET_CHAIN.blockExplorers.default.url}/tx/${hash}`} target="_blank" rel="noreferrer">view on explorer</a>
        </p>
      )}
      {newIds.length > 0 && (
        <div className="minted">
          <p><strong>Minted.</strong> Your new balloons:</p>
          <div className="minted-grid">
            {newIds.slice(0, 12).map((id) => (
              <figure key={id}>
                <img className="px" src={`/nft/images/${id}.png`} alt={`Elysium Balloon #${id}`} />
                <figcaption>#{id}</figcaption>
              </figure>
            ))}
          </div>
          {newIds.length > 12 && <p className="fine">+ {newIds.length - 12} more in your wallet</p>}
        </div>
      )}
      {connectOpen && <ConnectModal onClose={() => setConnectOpen(false)} />}
    </div>
  );
}
