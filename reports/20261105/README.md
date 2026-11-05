# LinkedIn performance, explained — 5 November 2026

[Open the report](index.html) after serving the repository locally. This revision clarifies the measures and adds a reaction/comment comparison. The analytical evidence remains the selected 279-post, 61-account reference sample, with counters captured 20–22 October 2026. Newer collected records have not been independently qualified into this sample.

## What each measure means

- **Reactions:** a combined count of LinkedIn reaction types, including Like, Celebrate, Support, Love, Insightful and Funny. The captured dataset does not split the count by type. It does not include comments.
- **Comments:** replies counted separately. A comment count is not a count of unique people, qualified buyers or sales.
- **Reposts:** shares; the counter was available for just 8 of 279 posts.
- **Impressions:** displays of a post. **Reach:** LinkedIn's estimate of distinct members and Pages who saw it. Neither was exposed in this dataset. We also have no observed clicks, saves, video views or sales.
- **Median:** the middle observed value after sorting. For an even number of observations, it is the average of the two middle values; 107.5 does not mean half a reaction occurred. Missing counters are unknown, not zero.

LinkedIn's [reaction guide](https://www.linkedin.com/help/linkedin/answer/a528190/use-linkedin-reactions?lang=en) and [post analytics definitions](https://www.linkedin.com/help/linkedin/answer/a6538517) explain the platform measures.

## What the sample says

Overall, 276 posts exposed reactions: median **107.5** and mean 417.45. Comments were available for 256 posts: median **36.5**. Ten posts account for 33.04% of observed reactions, so the mean is pulled upward by large posts. The reaction and comment medians use different observed groups.

| Format | Posts | Reaction counts observed | Median reactions | Comment counts observed | Median comments |
|---|---:|---:|---:|---:|---:|
| Text | 135 | 133 | 94 | 123 | 31 |
| Image | 111 | 110 | 186.5 | 106 | 57 |
| Video | 24 | 24 | 30 | 18 | 20 |
| Document | 9 | 9 | 178 | 9 | 14 |

Those comparisons combine different authors, topics and post ages. They do not establish that a format causes a result. Eleven authors have at least two image and two text posts; their median within-author difference is +26.5 reactions, with both positive and negative results. Topic, age and promotion still differ.

Among selected topics, personal-brand content had a median of 258 reactions across 53 observed counts; positioning had 179 across 39; AI-product education had 74.5 across 34. Teaching a method was the most common purpose: 91 posts, median 106 reactions. Stories had a median of 267 across 36 posts. These are ideas to test with your own audience, not live trend rankings.

The visual feature analysis covers only 36 posts using tags from existing descriptions. Framework/diagram tags cover 13 posts from four authors; screenshot/UI tags cover five from three authors. Tags overlap and have no matched feature-absent comparison. The 24 video reviews use sampled frames; no full video watch or audio review is documented. Do not interpret the feature medians as design effects.

For Outspoken, test posts built around one buyer question, a real founder decision, evidence and a lesson. Use the founder profile for perspective and the company page for product explanations and permissioned proof. Use a visual or video when it makes the explanation clearer. The [ten proposed carousels](../../publications/20261105/README.md) apply those ideas without claiming client results.

## Current collection status

On 4 November LinkedIn returned a security-verification page. The collector preserved the access hold and partial records. Subsequent scheduled runs have failed closed. The code now identifies the hold explicitly and avoids discovery/source requests while every LinkedIn consumer is held. This does not grant access or resume collection. The app's known permissions do not include post-read scopes. The official [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-09) requires approved access and the appropriate Page role or restricted member permissions; it is not a universal competitor search API.

The original [31 October report](../20261031/README.md) and its source data are preserved. This report is a new explanatory edition; no new engagement observations are asserted.
