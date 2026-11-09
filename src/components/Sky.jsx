import { useMemo } from "react";

// Balloons from the collection (sky removed) drift up behind the page at three depths.
export default function Sky() {
  const balloons = useMemo(() => {
    const n = typeof window !== "undefined" && window.innerWidth < 700 ? 9 : 16;
    return Array.from({ length: n }, (_, i) => {
      const depth = i % 3; // 0 far, 1 mid, 2 near
      return {
        id: 1 + ((i * 7 + Math.floor(Math.random() * 40)) % 40),
        left: (i / n) * 100 + Math.random() * (100 / n) - 4,
        size: [56, 92, 136][depth],
        dur: [46, 34, 25][depth] + Math.random() * 10,
        delay: -Math.random() * 40,
        sway: 6 + Math.random() * 14,
        depth,
      };
    });
  }, []);

  return (
    <div className="sky" aria-hidden="true">
      <div className="cloud c1" />
      <div className="cloud c2" />
      <div className="cloud c3" />
      {balloons.map((b, i) => (
        <div
          key={i}
          className={`drift d${b.depth}`}
          style={{ left: `${b.left}%`, width: b.size, animationDuration: `${b.dur}s`, animationDelay: `${b.delay}s`, "--sway": `${b.sway}px` }}
        >
          <img className="px" src={`${import.meta.env.BASE_URL}floaters/${b.id}.png`} alt="" loading="lazy" />
        </div>
      ))}
    </div>
  );
}
