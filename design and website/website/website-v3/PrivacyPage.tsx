import { Fragment, type ReactNode } from 'react';
import data from './privacy.json';
import './privacy.css';

/* Privacy and data-use page (DRAFT for owner and legal review).
   All copy lives in privacy.json. Square-bracket placeholders that start with "Owner to confirm:" are shown as marked notes. */

type Field = { label: string; text: string };
type Section = {
  id: string;
  heading: string;
  paragraphs?: string[];
  fields?: Field[];
  quote?: string;
  paragraphs_after?: string[];
};

const sections = data.sections as Section[];
const PLACEHOLDER = /(\[Owner to confirm:[^\]]*\])/g;

/** Wrap each "[Owner to confirm: ...]" placeholder in a visible mark; leave other text as it is. */
function withMarks(text: string): ReactNode {
  return text.split(PLACEHOLDER).map((part, i) =>
    part.startsWith('[Owner to confirm:')
      ? <mark key={i} className="privacy-todo">{part}</mark>
      : <Fragment key={i}>{part}</Fragment>
  );
}

function Paragraphs({ items }: { items?: string[] }) {
  if (!items) return null;
  return <>{items.map((p, i) => <p key={i}>{withMarks(p)}</p>)}</>;
}

export default function PrivacyPage() {
  const { meta, links } = data;
  return (
    <section className="privacy-page" aria-labelledby="privacy-title" data-block="privacy">
      <div className="privacy-page__inner">
        <a className="privacy-back" href={links.home_href}><span aria-hidden="true">←</span> {links.home_label}</a>

        <header className="privacy-head">
          <p className="eyebrow">{data.eyebrow}</p>
          <h1 id="privacy-title">{data.title}</h1>
          <p className="privacy-banner" role="note"><span className="privacy-banner__tag">Draft</span>{meta.banner}</p>
          {data.intro.map((p, i) => <p key={i} className="privacy-lede">{withMarks(p)}</p>)}
        </header>

        <div className="privacy-layout">
          <nav className="privacy-toc" aria-label={data.contents_label}>
            <p className="privacy-toc__label">{data.contents_label}</p>
            <ol>
              {sections.map(s => <li key={s.id}><a href={'#' + s.id}>{s.heading}</a></li>)}
              {meta.show_open_questions_on_page ? <li><a href="#open-questions">{data.open_questions_label}</a></li> : null}
            </ol>
          </nav>

          <div className="privacy-body">
            {sections.map(s => (
              <section key={s.id} id={s.id} className="privacy-section" aria-labelledby={s.id + '-h'}>
                <h2 id={s.id + '-h'}>{s.heading}</h2>
                <Paragraphs items={s.paragraphs} />
                {s.fields ? (
                  <dl className="privacy-fields">
                    {s.fields.map(f => (
                      <div key={f.label} className="privacy-fields__row">
                        <dt>{f.label}</dt>
                        <dd>{withMarks(f.text)}</dd>
                      </div>
                    ))}
                  </dl>
                ) : null}
                {s.quote ? <blockquote className="privacy-quote"><p>{s.quote}</p></blockquote> : null}
                <Paragraphs items={s.paragraphs_after} />
              </section>
            ))}

            {meta.show_open_questions_on_page ? (
              <section id="open-questions" className="privacy-section privacy-open" aria-labelledby="open-questions-h">
                <h2 id="open-questions-h">{data.open_questions_label}</h2>
                <p>{data.open_questions_note}</p>
                <ol>
                  {data.open_questions.map((q, i) => <li key={i}>{q}</li>)}
                </ol>
              </section>
            ) : null}

            <p className="privacy-meta">Draft prepared {meta.prepared}.</p>

            <div className="privacy-actions">
              <a className="os-btn" href={links.contact_href}>{links.contact_label}</a>
              <a className="os-btn os-btn--outline" href={links.home_href}>{links.home_label}</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
