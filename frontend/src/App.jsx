import { useEffect, useMemo, useRef, useState } from "react";
import { ArrowRight, Braces, Check, CircleHelp, Image as ImageIcon, Search, Sparkles, X } from "lucide-react";
import { catalog, categories } from "./catalog.js";
import { rankImages } from "./search.js";
import "./App.css";

const suggestions = ["quiet alpine lake", "modern office with sunlight", "bold portrait in red", "coffee among green plants"];

function Logo() {
  return <a className="brand" href="#top" aria-label="VisionQuery home"><span className="brand-mark" aria-hidden="true"><span /></span><span>VisionQuery</span></a>;
}

function ResultCard({ image, index, onSelect }) {
  const score = image.score == null ? null : Math.round(image.score * 100);
  return (
    <article className={`result-card result-card--${image.orientation}`} style={{ "--delay": `${index * 45}ms` }}>
      <button type="button" className="image-button" onClick={() => onSelect(image)} aria-label={`View ${image.title}`}>
        <img src={image.src} alt={image.description} loading={index > 3 ? "lazy" : "eager"} />
        <span className="image-index">{String(index + 1).padStart(2, "0")}</span>
        {score !== null && <span className="match-badge"><Check size={13} strokeWidth={2.4} /> {score}% match</span>}
      </button>
      <div className="card-copy"><p>{image.eyebrow}</p><h3>{image.title}</h3></div>
    </article>
  );
}

function DetailDialog({ image, onClose }) {
  const closeRef = useRef(null);
  useEffect(() => {
    if (!image) return undefined;
    closeRef.current?.focus();
    const onKeyDown = (event) => event.key === "Escape" && onClose();
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [image, onClose]);
  if (!image) return null;
  const score = image.score == null ? null : Math.round(image.score * 100);
  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <section className="detail-dialog" role="dialog" aria-modal="true" aria-labelledby="detail-title">
        <button ref={closeRef} type="button" className="close-button" onClick={onClose} aria-label="Close image preview"><X size={20} /></button>
        <div className="detail-image-wrap"><img src={image.src} alt={image.description} /></div>
        <div className="detail-copy">
          <div className="detail-kicker"><span>{image.category}</span>{score !== null && <span>{score}% semantic match</span>}</div>
          <h2 id="detail-title">{image.title}</h2><p>{image.description}</p>
          <div className="tag-row" aria-label="Image concepts">{image.tags.slice(0, 6).map((tag) => <span key={tag}>{tag}</span>)}</div>
        </div>
      </section>
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [category, setCategory] = useState("All");
  const [selected, setSelected] = useState(null);
  const results = useMemo(() => rankImages(catalog, submittedQuery, category), [submittedQuery, category]);
  const submitSearch = (event) => { event?.preventDefault(); setSubmittedQuery(query.trim()); };
  const trySuggestion = (value) => { setQuery(value); setSubmittedQuery(value); };
  const clearSearch = () => { setQuery(""); setSubmittedQuery(""); setCategory("All"); };

  return (
    <div id="top" className="site-shell">
      <header className="site-header">
        <Logo />
        <nav aria-label="Primary navigation">
          <a href="#collection">Collection</a><a href="#method">How it works</a>
          <a className="nav-cta" href="https://github.com/aaryabookseller16/Vision-Query" target="_blank" rel="noreferrer">View code <ArrowRight size={15} /></a>
        </nav>
      </header>
      <main>
        <section className="search-stage" aria-labelledby="page-title">
          <div className="stage-meta"><span>Multimodal search lab</span><span className="live-dot">10 images indexed</span></div>
          <h1 id="page-title">Find the image<br /><em>you mean.</em></h1>
          <p className="stage-intro">Search ideas, moods and scenes—not file names. VisionQuery turns natural language into visual discovery.</p>
          <form className="search-form" onSubmit={submitSearch} role="search">
            <Search size={22} aria-hidden="true" /><label className="sr-only" htmlFor="vision-search">Describe the image you are looking for</label>
            <input id="vision-search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Describe a scene, subject or mood…" autoComplete="off" />
            {query && <button className="input-clear" type="button" onClick={() => setQuery("")} aria-label="Clear search"><X size={18} /></button>}
            <button className="search-submit" type="submit">Search <ArrowRight size={18} /></button>
          </form>
          <div className="suggestions" aria-label="Suggested searches"><span>Try</span>{suggestions.map((suggestion) => <button key={suggestion} type="button" onClick={() => trySuggestion(suggestion)}>{suggestion}</button>)}</div>
          <div className="signal-line" aria-hidden="true"><span /><i /><i /><i /><i /><i /><i /></div>
        </section>

        <section id="collection" className="collection-section" aria-labelledby="collection-title">
          <div className="section-heading"><div><p className="section-kicker">Curated demo index</p><h2 id="collection-title">{submittedQuery ? <>Results for “{submittedQuery}”</> : "Explore the collection"}</h2></div><p className="result-count">{results.length} {results.length === 1 ? "image" : "images"}</p></div>
          <div className="filter-row" aria-label="Filter by category">{categories.map((item) => <button key={item} type="button" className={category === item ? "is-active" : ""} onClick={() => setCategory(item)}>{item}</button>)}</div>
          {results.length > 0 ? <div className="results-grid">{results.map((image, index) => <ResultCard key={image.id} image={image} index={index} onSelect={setSelected} />)}</div> : (
            <div className="empty-state"><CircleHelp size={32} /><h3>No close concept match</h3><p>Try a broader subject, colour, place or mood—or return to the full collection.</p><button type="button" onClick={clearSearch}>Reset search</button></div>
          )}
        </section>

        <section id="method" className="method-section" aria-labelledby="method-title">
          <div className="method-copy"><p className="section-kicker">Under the surface</p><h2 id="method-title">Language and imagery,<br />in the same space.</h2><p>The local API uses a pretrained CLIP model to map text and images into comparable vectors. The hosted showcase mirrors the retrieval flow over a small, transparent concept index so it stays fast and dependable on the web.</p><a href="https://github.com/aaryabookseller16/Vision-Query" target="_blank" rel="noreferrer">Read the architecture <ArrowRight size={17} /></a></div>
          <ol className="method-steps">
            <li><span><ImageIcon size={19} /></span><div><b>01</b><h3>Index imagery</h3><p>Images become normalized vectors with searchable metadata.</p></div></li>
            <li><span><Braces size={19} /></span><div><b>02</b><h3>Understand language</h3><p>Your phrase is mapped into the same conceptual space.</p></div></li>
            <li><span><Sparkles size={19} /></span><div><b>03</b><h3>Rank by meaning</h3><p>Cosine similarity brings the closest visual ideas to the top.</p></div></li>
          </ol>
        </section>
      </main>
      <footer><Logo /><p>Open-source multimodal retrieval, presented with clarity.</p><span>© 2026 VisionQuery</span></footer>
      <DetailDialog image={selected} onClose={() => setSelected(null)} />
    </div>
  );
}
