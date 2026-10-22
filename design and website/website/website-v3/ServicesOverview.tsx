import content from "./content.json";
import "./services-overview.css";

type ServicesOverviewProps = {
  children?: import("react").ReactNode;
};

const services = content.services.modules;

export function ServicesOverview({ children }: ServicesOverviewProps) {
  return (
    <>
      <section className="services-overview section" aria-labelledby="services-overview-title">
        <header className="services-overview__heading">
          <p className="eyebrow">{content.services.eyebrow}</p>
          <h1 id="services-overview-title">{content.services.title}</h1>
        </header>

        <div className="services-overview__grid">
          {services.map((service) => (
            <article className="services-overview__item" key={service.id}>
              <details className="services-overview__details">
                <summary className="services-overview__summary">
                  <span className="services-overview__number" aria-hidden="true">{service.number}</span>
                  <span className="services-overview__summary-copy">
                    <span className="services-overview__title">{service.title}</span>
                    <span className="services-overview__short">{service.short}</span>
                  </span>
                  <span className="services-overview__chevron" aria-hidden="true" />
                </summary>
                <div className="services-overview__expanded">
                  <p className="services-overview__body">{service.body}</p>
                  <h2>Deliverables</h2>
                  <ul>
                    {service.deliverables.map((deliverable) => (
                      <li key={deliverable}>{deliverable}</li>
                    ))}
                  </ul>
                  <p className="services-overview__boundary">
                    <strong>Scope and permissions</strong>
                    <span>{service.boundary}</span>
                  </p>
                </div>
              </details>
            </article>
          ))}
        </div>
      </section>
      {children}
    </>
  );
}
