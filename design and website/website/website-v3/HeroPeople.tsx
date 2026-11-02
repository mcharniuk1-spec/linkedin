// Hero helpers (V10, proposed): the "selected text" accent on one word and the people strip with the graded hero portraits.
const base = '/assets/library-r12/thumbs/';

/** One accent word per headline: marker fill, dashed selection outline and four corner handles. */
export function Sel({children}: {children: string}) {
  return <span className="sel">{children}<i aria-hidden="true" /><i aria-hidden="true" /><i aria-hidden="true" /><i aria-hidden="true" /></span>;
}

/** Fictional founders (graded hero portraits) next to the audience line; the label keeps the disclosure visible. */
export function HeroPeople({className = 'audience-line'}: {className?: string}) {
  return (
    <div className="hero-people">
      <span className="hero-people__faces" aria-hidden="true">
        <img src={base + 'thumb-01.webp'} alt="" width="40" height="40" />
        <img src={base + 'thumb-04.webp'} alt="" width="40" height="40" />
        <img src={base + 'thumb-03.webp'} alt="" width="40" height="40" />
      </span>
      <p className={className}>Illustrative founders · Europe-based B2B AI SaaS · Seed to Series B</p>
    </div>
  );
}
