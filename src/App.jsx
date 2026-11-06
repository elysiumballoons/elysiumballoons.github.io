import Sky from "./components/Sky";
import MintPanel from "./components/MintPanel";
import GetHype from "./components/GetHype";
import Gallery from "./components/Gallery";
import Rarity from "./components/Rarity";
import { WalletButton } from "./components/Wallet";
import { CONTRACT_ADDRESS, TARGET_CHAIN, X_URL } from "./config";

export default function App() {
  return (
    <>
      <Sky />
      <header className="nav">
        <a href="#top" className="brand">
          <img className="px" src="/nft/images/1.png" alt="" />
          <span>Elysium Balloons</span>
        </a>
        <nav className="links">
          <a href="#mint">Mint</a>
          <a href="#hype">Get HYPE</a>
          <a href="#gallery">Gallery</a>
          <a href="#traits">Traits</a>
        </nav>
        <WalletButton />
      </header>

      <main id="top">
        <section className="hero">
          <div className="hero-copy">
            <h1 className="title" aria-label="Elysium Balloons">
              <span className="t1">Elysium</span>
              <span className="t2">Balloons</span>
            </h1>
            <p className="lede">
              10,000 pixel balloons, each with its own face, drifting over Elysium — the HYPE layer 2.
              Pick a few, cut the string, watch them float into your wallet.
            </p>
            <ul className="facts">
              <li><strong>10,000</strong> balloons</li>
              <li><strong>0.01</strong> HYPE each</li>
              <li><strong>{TARGET_CHAIN.name}</strong> chain {TARGET_CHAIN.id}</li>
            </ul>
          </div>
          <MintPanel />
        </section>

        <GetHype />
        <Gallery />
        <Rarity />
      </main>

      <footer className="foot">
        <div className="ground" aria-hidden="true" />
        <div className="foot-inner">
          <span>Elysium Balloons · on {TARGET_CHAIN.name}</span>
          {CONTRACT_ADDRESS && (
            <a href={`${TARGET_CHAIN.blockExplorers.default.url}/address/${CONTRACT_ADDRESS}`} target="_blank" rel="noreferrer">Contract</a>
          )}
          <a href={X_URL} target="_blank" rel="noreferrer">X</a>
        </div>
      </footer>
    </>
  );
}
