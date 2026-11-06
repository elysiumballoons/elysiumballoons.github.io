import { useEffect, useState } from "react";
import { COLLECTION_SIZE } from "../config";

const pick = (n) => {
  const s = new Set();
  while (s.size < n) s.add(1 + Math.floor(Math.random() * COLLECTION_SIZE));
  return [...s];
};

export default function Gallery() {
  const [ids, setIds] = useState(() => pick(18));
  const [q, setQ] = useState("");
  const [sel, setSel] = useState(null);
  const [meta, setMeta] = useState(null);

  useEffect(() => {
    if (!sel) return;
    setMeta(null);
    fetch(`/nft/metadata/${sel}.json`).then((r) => r.json()).then(setMeta).catch(() => setMeta({ attributes: [] }));
    const onKey = (e) => e.key === "Escape" && setSel(null);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [sel]);

  const find = (e) => {
    e.preventDefault();
    const n = parseInt(q, 10);
    if (n >= 1 && n <= COLLECTION_SIZE) setSel(n);
  };

  return (
    <section className="section gallery" id="gallery">
      <div className="gallery-head">
        <h2>Meet the flock</h2>
        <form onSubmit={find} className="find">
          <input aria-label="Balloon number" placeholder="Balloon # (1–10000)" value={q} onChange={(e) => setQ(e.target.value.replace(/\D/g, ""))} />
          <button className="btn btn-ink btn-sm">Look up</button>
        </form>
        <button className="btn btn-paper btn-sm" onClick={() => setIds(pick(18))}>Show others</button>
      </div>
      <div className="grid">
        {ids.map((id) => (
          <button key={id} className="tile" onClick={() => setSel(id)} aria-label={`Open balloon #${id}`}>
            <img className="px" src={`/nft/images/${id}.png`} alt="" loading="lazy" />
            <span>#{id}</span>
          </button>
        ))}
      </div>

      {sel && (
        <div className="modal-back" onClick={() => setSel(null)}>
          <div className="modal modal-wide pixel-box" role="dialog" aria-label={`Balloon #${sel}`} onClick={(e) => e.stopPropagation()}>
            <img className="px detail-img" src={`/nft/images/${sel}.png`} alt={`Elysium Balloon #${sel}`} />
            <div className="detail">
              <div className="modal-head">
                <h3>{meta?.name || `Elysium Balloon #${sel}`}</h3>
                <button className="icon-btn" onClick={() => setSel(null)} aria-label="Close">✕</button>
              </div>
              <dl className="traits">
                {(meta?.attributes || []).filter((a) => a.value !== "None").map((a) => (
                  <div key={a.trait_type}><dt>{a.trait_type}</dt><dd>{a.value}</dd></div>
                ))}
              </dl>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
