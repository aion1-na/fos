import Link from "next/link";

export default function HomePage() {
  return (
    <main className="atlas-shell">
      <header>
        <p className="eyebrow">FOS Atlas</p>
        <h1>Dataset directory</h1>
        <p className="lede">
          Request-status metadata, fixture hashes, licenses, and dataset cards for the data workstream.
        </p>
      </header>
      <Link className="primary-link" href="/datasets">
        View datasets
      </Link>
      <Link className="primary-link" href="/ai-exposure">
        View AI exposure
      </Link>
      <Link className="primary-link" href="/gfs">
        View GFS Wave 1
      </Link>
    </main>
  );
}
