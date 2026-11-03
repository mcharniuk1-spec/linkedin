# LinkedIn publications R15 for the OUTSPOKEN profile (drafts, proposed), 2 November 2026

Status: two drafts, one per new film, for the founders to edit and approve. **Nothing is published or scheduled, and nothing is written to Figma:** Claude's connection to the owner's Figma plan (Genoa) is a View seat (`whoami`, 2 November 2026), so the placement in Figma is specified below for someone with an edit seat. Facts come from the repository records; no client, result, quote or statistic is invented.

## Reader, job and format
- **Reader:** founders of Europe-based B2B AI SaaS companies (10 to 50 people, seed to Series B) who know their product better than anyone and want buyers to understand it.
- **Job of each post:** show how the work goes, in one clear idea, before any offer. Offer posts had the lowest median reactions of the five purposes in the reference sample (`TOPICS-AND-PUBLICATIONS-R12.md`: offers 67 over 63 posts, methods 106 over 91 posts, stories 267 over 36 posts; descriptive, not causal), so neither draft leads with prices; both state that the prices in the film are indicative and send the reader to the booking block on the website.
- **Format:** native video upload with captions on. In the reference sample the video group was small (24 posts) and the authors differ, so the medians prove nothing about video; the drafts therefore lead with one idea in the first two lines. Posts are descriptive, not a forecast: reach, impressions and sales are not promised.
- **Voice:** first person plural, short sentences, no hype. The protected hero line and call to action are used exactly as on the website: "Make the right buyers care about you and what you’re building." and "Book an intro call".

## Order
1. **L3, the launch film in 4:5** (the feed format; 42 s). 2. **L4, the OS motion film in 16:9** (28 s), a few days later. They continue the series in `PUBLICATIONS-R14.md`: L1 and L2 used the R14 films (16:9 launch, 4:5 OS motion); L3 and L4 use the two new R15 compositions in the other aspect ratios.

## L3: launch film, 4:5, 42 s (`film/launch-r15/build_4x5.py`)
**Post text (801 characters):**

```
Your best material is already in your work: the decisions you make, the questions you answer, the trade-offs you accept.

This 42-second film shows how we turn it into LinkedIn content that buyers can use. We start with what you know and interview you about how you build and decide. Together we find one clear position, map the market and the questions your buyers ask, and plan the ideas, evidence and formats. Then we shape them into content in your voice, prepare the next conversation and review the response.

The film ends on three starting points. The prices on screen are indicative; the final scope is confirmed together.

We help Europe-based B2B AI SaaS founders do this. Make the right buyers care about you and what you’re building.

Book an intro call: the link is in the first comment.
```

**Hashtags:** `#FounderLedMarketing #B2BSaaS #LinkedInMarketing`

**First comment:** The website, with the booking block: <site address>/#contact  (the website's booking block; use the production address once the owner launches it. The review edition, https://outspoken-voice-7c4e2.vercel.app/, is not indexed and is for review only.)

**Media:** the 4:5 master with the owner's recorded voice (the repository master carries music and effects only), captions on; poster frame 0.00 s.

**Sources:** the film's README (stages and narration windows), `content.json` (protected hero line and call to action), `pricing.json` (`public_label`: "Indicative packages — final scope confirmed together"). Every statement in the post is a description of what the film shows or of the approved positioning; nothing about results.

## L4: OS motion film, 16:9, 28 s (`film/motion-os-r15/build_16x9.py`)
**Post text (537 characters):**

```
Two letters, cut like a stencil. One slash that marks the point.

We use our own mark the way we work with a founder’s material: gather the thinking, open it into an interview, cut the notes down to one clear position, then turn that position into a plan and a post.

This 28-second film follows the mark through those steps, on to the buyer conversation and three starting points. The prices on screen are indicative.

Make the right buyers care about you and what you’re building.

Book an intro call: the link is in the first comment.
```

**Hashtags:** `#BrandIdentity #FounderLedMarketing`

**First comment:** The website, with the booking block: <site address>/#contact  (same note as L3).

**Media:** the 16:9 master with the owner's recorded voice, captions on; poster frame 0.00 s.

**Sources:** the film's README, `content.json`, `pricing.json`. The first two lines echo the R14 draft L2 ("Two letters, cut like a stencil") and describe the OS stencil identity that the owner kept on 2 November 2026; that choice is a selection, not an acceptance of the identity.

## Website reuse in the final delivery
Both drafts use the website's own wording (the protected hero line and call to action, the indicative-packages label) and send the reader to its booking block, so the post, the film and the page make the same promise. The films can be embedded on the website later; that is a separate website change and is not part of this round. The booking block is reached at `<site address>/#contact` (the site is one page; `/contact` redirects to it).

## Before posting
- Record the voice from `film/launch-r15/4x5/VOICEOVER.md` and `film/motion-os-r15/16x9/VOICEOVER.md`; the windows keep the picture in sync, and a take may be shorter than its window, never longer.
- Check every statement against the current repository and the website at the time of posting; confirm the production address for the first comment.
- Author approval of voice and facts (owner acceptance of the films and of the identity is still false).
- Measure per post: reactions, comments, qualified replies and profile visits, kept separate as `TOPICS-AND-PUBLICATIONS-R12.md` describes. Nothing in this repository posts, schedules or advertises.

## Placement in Figma (to be done by someone with an edit seat; not done)
Existing file `m7zSeYVpEI88i9qwTrnUQt`, page "Applications" (`2:3`), where the 20 native publication components P01 to P20 live (`editorial/figma/FRAME-MAP.md`).
1. Duplicate the video-post component **P14** (`176:1046`) twice and place the copies after **P20** (`176:1190`) in the production area (`176:1210`). Name them `L3 launch film 4:5 (R15)` and `L4 OS motion film 16:9 (R15)`.
2. In each copy set the body text layer (P14's is `176:1053`) to the exact text above, the hashtag layer (`185:1001`) to the hashtags, the author instance (`176:1047`) to the chosen profile, and fill the poster rectangle (`176:1055`) with the poster frame exported from the committed master (`ffmpeg -ss 0 -i <master> -frames:v 1 poster.png`). Keep all text editable and leave the LinkedIn chrome as in P14.
3. Check each body against the `bodySha256`, `bodyCharacters` and `bodyUtf8Bytes` below (UTF-8, line breaks as `\n`, no trailing newline, hashtags and first comment excluded, as in `editorial/figma/FRAME-MAP.json`).
4. Record the new node IDs and URLs in the JSON block below (a copy of this file's block, not `FRAME-MAP.json`, whose verifier expects exactly 20 posts).

```json
{
  "status": "proposed; nothing is posted; nothing is written to Figma (Claude's seat on plan Genoa is View)",
  "date": "2026-11-02",
  "figma": {
    "fileKey": "m7zSeYVpEI88i9qwTrnUQt",
    "pageId": "2:3",
    "libraryId": "176:725",
    "productionId": "176:1210",
    "cloneFrom": {
      "id": "P14",
      "nodeId": "176:1046",
      "bodyNodeId": "176:1053",
      "authorInstanceId": "176:1047",
      "mediaSlotId": "176:1054",
      "posterRectangleId": "176:1055",
      "hashtagNodeIds": [
        "185:1001"
      ]
    },
    "placeAfter": {
      "id": "P20",
      "nodeId": "176:1190"
    }
  },
  "posts": [
    {
      "id": "L3",
      "title": "Launch film, 4:5, 42 s",
      "format": "video",
      "proposedAuthor": "a founder's personal profile (the owner chooses; the company page may reshare)",
      "frameName": "L3 launch film 4:5 (R15)",
      "bodySha256": "260a5d8dd1ea2c1311e2e5005c1b90bf13e9c01fb6233b20016434da5c64aec8",
      "bodyCharacters": 801,
      "bodyUtf8Bytes": 803,
      "hashtags": "#FounderLedMarketing #B2BSaaS #LinkedInMarketing",
      "firstComment": "The website, with the booking block: <site address>/#contact",
      "master": {
        "file": "design and website/assets/film-r15/launch-r15-4x5-master.mp4",
        "bytes": 7596445,
        "sha256": "d221aeb81d06a11c5f633a69ab914857f494a668c954ba2fc5ce0b178ab2aad0"
      },
      "posterFrame": "frame at 0.00 s of the master (the OS mark on navy), exported at 1080x1350",
      "sources": [
        "design and website/film/launch-r15/4x5/README.md",
        "design and website/website/website-v3/content.json#protected",
        "design and website/website/website-v3/pricing.json#public_label"
      ],
      "approval": "Draft; the founder must review voice and facts and record the voice before publication."
    },
    {
      "id": "L4",
      "title": "OS motion film, 16:9, 28 s",
      "format": "video",
      "proposedAuthor": "a founder's personal profile (the owner chooses; the company page may reshare)",
      "frameName": "L4 OS motion film 16:9 (R15)",
      "bodySha256": "fad4d31f5d60bbc5311c940b040a29cb3662c407fe9ea3b7d076e16d2d999e8d",
      "bodyCharacters": 537,
      "bodyUtf8Bytes": 541,
      "hashtags": "#BrandIdentity #FounderLedMarketing",
      "firstComment": "The website, with the booking block: <site address>/#contact",
      "master": {
        "file": "design and website/assets/film-r15/os-motion-r15-16x9-master.mp4",
        "bytes": 6208384,
        "sha256": "9b550f52a4b333800955e4abf04497161289863d66d21afc3fb3f9eda042a120"
      },
      "posterFrame": "frame at 0.00 s of the master (the thought field on navy), exported at 1920x1080",
      "sources": [
        "design and website/film/motion-os-r15/16x9/README.md",
        "design and website/website/website-v3/content.json#protected",
        "design and website/website/website-v3/pricing.json#public_label"
      ],
      "approval": "Draft; the founder must review voice and facts and record the voice before publication."
    }
  ]
}
```
