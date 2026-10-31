// Hero helpers (V10, proposed): the "selected text" accent on one word and the people strip with the graded hero portraits.
const base = '/assets/identity/v10/heroes/';

/** One accent word per headline: marker fill, dashed selection outline and four corner handles. */
export function Sel({children}: {children: string}) {
  return <span className="sel">{children}<i aria-hidden="true" /><i aria-hidden="true" /><i aria-hidden="true" /><i aria-hidden="true" /></span>;
}

/** Fictional founders (graded hero portraits) next to the audience line; the label keeps the disclosure visible. */
export function HeroPeople({className = 'audience-line'}: {className?: string}) {
  return (
    <div className="hero-people">
      <span className="hero-people__faces" aria-hidden="true">
        <img src={base + 'h3-avatar-a.webp'} alt="" width="40" height="40" />
        <img src={base + 'h4-avatar-b.webp'} alt="" width="40" height="40" />
        <img src={base + 'h2-founder.webp'} alt="" width="40" height="40" style={{objectPosition: '56% 22%'}} />
      </span>
      <p className={className}>Illustrative founders · Europe-based B2B AI SaaS · Seed to Series B</p>
    </div>
  );
}
