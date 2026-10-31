import all from './reviews.json';

/** Curated short set of the fifteen fictional sample emails. The full library stays in reviews.json. */
export const curatedIds=['sample-email-01','sample-email-03','sample-email-04','sample-email-05','sample-email-09','sample-email-13'];
export const opinions=(all as any[]).filter(email=>curatedIds.includes(email.id));
export const opinionCount=opinions.length;
