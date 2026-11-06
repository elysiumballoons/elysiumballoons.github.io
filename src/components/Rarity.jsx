import { useEffect, useState } from "react";

const ORDER = ["Balloon", "Color", "Pattern", "Eyes", "Mouth", "Headwear", "Eyewear", "Sky", "Sky Extra", "Clouds", "Cheeks", "Legendary"];

export default function Rarity() {
  const [data, setData] = useState(null);
  const [cat, setCat] = useState("Balloon");
  useEffect(() => { fetch("/nft/traits.json").then((r) => r.json()).then(setData).catch(() => {}); }, []);
  if (!data) return null;

  const rows = Object.entries(data.traits[cat] || {}).sort((a, b) => b[1] - a[1]);
  const max = rows[0]?.[1] || 1;
  return (
    <section className="section rarity" id="traits">
      <h2>What’s in the sky</h2>
      <p className="lede">Twelve trait groups, five one-of-one legends, no two balloons alike.</p>
      <div className="cats">
        {ORDER.filter((k) => data.traits[k]).map((k) => (
          <button key={k} className={`chip ${k === cat ? "on" : ""}`} onClick={() => setCat(k)}>{k}</button>
        ))}
      </div>
      <ul className="bars">
        {rows.map(([name, n]) => (
          <li key={name}>
            <span className="bars-name">{name}</span>
            <span className="bars-track"><span style={{ width: `${(n / max) * 100}%` }} /></span>
            <span className="bars-pct">{((n / data.total) * 100).toFixed(n / data.total < 0.01 ? 2 : 1)}%</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
