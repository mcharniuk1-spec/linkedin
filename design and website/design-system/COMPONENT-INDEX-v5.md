# OUTSPOKEN — current V5 component source index

## Current V5 additions

The selected identity is study01: the solid capsule microphone with two wrapped silver bands and one upright rib. The brand word is always uppercase OUTSPOKEN. Use the exact outlined Archivo source with its custom first O; use mono navy for a small reading signature. The V4 selected004 remains historical only.

| Current source | Exact scope and role |
| --- | --- |
| [Identity manifest](../brand-library/packages/assets/revisions/v5/identity/manifest.json) | Eight preserved source studies; five wordmark treatments; six actual native model views. Transparent reference-derived artwork and GLB renders are separate representations. |
| [Gallery manifest](../brand-library/packages/showcase-v5/manifest.json) | 210 button variants, 24 media compositions, 19 editable templates, five people directions and 108 retained object views. |
| [Gallery exports](../brand-library/packages/showcase-v5/index.ts) | BrandStudio, StudioButton, MediaFrame, banners, blocks, schemas, annotations, post/email/feedback/caption specimens. |
| [Object views](../brand-library/packages/assets/revisions/v5/objects/manifest.json) | Twenty-five objects and eleven word sculptures, each with front, left and right PNG views. Original GLBs remain in the source archive. |
| [Film manifest](../brand-library/packages/video/revisions/v5/manifest.json) | Three original 18-second silent films: landscape, square and portrait. These are distinct from website scroll choreography. |
| [Prepared native data]([dated-local-evidence-omitted]) | Measured editable text, shapes, image slots and vector references. Execution is established separately by root Figma receipts. |

## Current and retained native boards

The existing file has three pages. These are source-backed imported boards and masters; the [V5 final readback]([dated-local-evidence-omitted]) passed 376/376 scoped checks and the [current native map](../brand-library/design/v5-figma-map.json) binds the exact IDs. Independent live native reviews are recorded separately. A parent board is a navigation anchor, not another reusable component. Retained V3/V4 sources remain clearly versioned; current V5 styling takes precedence where applied.

| Family | Source version and finite scope | Native board / master and receipt |
| --- | --- | --- |
| Current V5 banners and blocks | Three banner templates and four distinct text blocks; banners are contextual block assemblies, not a duplicate component taxonomy | Component receipt maps: `OS5-BN-rule`140:1868, `OS5-BN-split`140:1877, `OS5-BN-signal`140:1886; four block masters140:1900,140:1910,140:1920,140:1929. [V5 receipts]([dated-local-evidence-omitted]) |
| Retained banner catalog | Eleven native editable layouts; `catalog-v3` version4 brand refresh, retained source contract | Board83:750, set83:946. [Original import receipt]([dated-local-evidence-omitted]) |
| Current V5 schemas | Two semantic editable schemas: process and approval; meaningful native nodes, labels and connectors | `OS5-SC-process`140:1938; `OS5-SC-approval`140:1959. [V5 receipts]([dated-local-evidence-omitted]) |
| Retained schema catalog | Eleven native editable layouts; original catalog source preserved rather than duplicated | Board87:1607, set87:2139. [Original import receipt]([dated-local-evidence-omitted]) |
| Current V5 controls | Fourteen color/type sets × fifteen edge/pose variants =210 | Page 2:2; set IDs140:125 through140:1620 are mapped individually in the [actual V5 batch receipts]([dated-local-evidence-omitted]) |
| Current V5 media and people |24 media components in eight sets; five people directions; six native identity views | Page 2:2 current batch receipts, with explicit image-fill/raster and2D-pose boundaries |
| Current V5 identity and words | Eight preserved study directions; five exact vector wordmark components; six native rendered views | Page 0:1 lead129:46; wordmark components138:2,138:15,139:2,139:15,139:28. [Wordmark receipts]([dated-local-evidence-omitted]) |
| Current V5 object views | Thirty-six stable subjects × three poses =108image components; GLBs remain source geometry | Page 2:2;36sets from131:18 through131:473. [Object receipts]([dated-local-evidence-omitted]) |

Do not count the new19templates and retained88layouts as a replacement for the64 baseline UI family contracts. Choose the current V5 component for new work; use a retained layout when its job fits, then explicitly reconcile current identity/source dependencies. Schema arrows represent real relationships; customer outcomes remain fictional unless sourced and permissioned.

## Retained baseline source contracts

The baseline64 UI families and88 catalog layouts below remain available. Current V5 identity and showcase sources take precedence for current artwork and expanded controls. The baseline ThreeTiltButton API is separate from StudioButton's seven-color, five-edge, three-pose matrix. Retained story IDs describe source coverage; they are not a new exhaustive V5 runtime acceptance claim. Native Figma, React runtime, SVG masters and static exports remain distinct representations. Owner acceptance is separate.

## All button options and interaction states

These are source-supported options, not a catalogue of invented sizes or effects. `hover`, `pressed` and `focus` are native interactions; they are not boolean component props.

| Control | Actual API options | Actual states / boundary | Story IDs |
| --- | --- | --- | --- |
| ThreeTiltButton | variant: primary / secondary / quiet; tone: navy / marigold / silver; arrow:true/false; loading; disabled; typed native button props | 9 tone×variant pairs. Native hover/press/focus, spring reset, loading+disabled block activation; reduced motion/touch stay flat; offscreen renderer release. Variant secondary defaults to silver when tone is omitted; quiet removes the outer shadow. No outline,size or error variant is declared. | experience-v4-button-catalog--playground; --all-tone-variant-combinations; --disabled-matrix; --loading-matrix; --focus-and-keyboard; --arrow-options; --long-label |
| ActionButton (OS-C008) | variant: primary / secondary / quiet; loading; disabled; native button props | Default, native hover/press/focus, loading indicator, disabled. loading also disables; reduced motion stops tilt/spinner. Long labels are a real story. No tone or size prop. | actions-actionbutton--default; --states; --long-label |
| IconButton (OS-C010) | label required; icon: arrow / close / plus / check / chat / play / chevron / mail / source; native button props | Accessible name and native focus/disabled. No dedicated loading,tone or variant prop. | actions-iconbutton--default |
| TextLink (OS-C009) | children; href optional | href supplied: link. Missing href: inert destination-pending text; not a fake working button. | actions-textlink--default |
| NavigationHeader menu (OS-C018) | items; ctaHref | Native phone Menu toggle, aria-expanded/controls; source CTA uses TextLink. | navigation-navigationheader--default |
| ChatLauncher (OS-C032) | onClick; expanded false/true | Native button plus aria-expanded. Interface demo only. | chat-chatlauncher--default |
| ChatComposer (OS-C035) | value; onChange; onSend; disabled | Send disabled when empty/whitespace or caller disabled. TextArea maxLength2000. No external messaging service. | chat-chatcomposer--default |
| ChatStatusActions (OS-C036) | state: idle / sending / waiting / error / offline / handoff / resolved; onRetry; onResolve | Retry shown in error; Close conversation in idle with onResolve. Both use ActionButton. | chat-chatstatusactions--default |
| PaginationSeries (OS-C051) | page; total; onChange | Previous disabled at page≤1; Next disabled at page≥total. Native labels and live page status. | editorial-paginationseries--default |
| PerspectiveVideo controls | tilt:left/right; autoPlayOnOpen false/true; poster,src,title,description,caption,onOpenChange | Watch trigger,Close,Escape,backdrop. Explicit activation mounts video; opt-in autoplay is muted. Focus restored to original trigger. | experience-v3-perspective-media--left-plate; --right-plate |

Nine real ThreeTiltButton pairs: `primary/navy`, `primary/marigold`, `primary/silver`, `secondary/navy`, `secondary/marigold`, `secondary/silver`, `quiet/navy`, `quiet/marigold`, `quiet/silver`. Disabled and loading matrices each contain the same nine pairs. The focus matrix uses actual focus and keyboard navigation; it does not paint a fake focused state.

[V4 button stories](../brand-library/packages/experience-v3/stories/ExperienceV4Buttons.stories.tsx) · [Three.js button implementation](../brand-library/packages/experience-v3/ThreeTiltButton.tsx) · [baseline native action source](../brand-library/packages/ui/src/foundations.tsx)

## All64 registered UI component families

The record’s named states below are its source story variants. They do not mean that every variation was newly revalidated for V4. The TypeScript source owns props and defaults.

| ID | Component / source | Typed props/defaults | Recorded story variants | Exact story IDs |
| --- | --- | --- | --- | --- |
| OS-C001 | [Container](../brand-library/packages/ui/src/foundations.tsx) | {children,className='',narrow=false}:ChildrenProps&{narrow?:boolean} | default | `foundations-container--default` |
| OS-C002 | [StackGrid](../brand-library/packages/ui/src/foundations.tsx) | {children,columns=2,gap=24,align='start'}:ChildrenProps&{columns?:1 / 2 / 3 / 4;gap?:16 / 24 / 32 / 48;align?:'start' / 'center' / 'end'} | default | `foundations-stackgrid--default` |
| OS-C003 | [SurfacePlate](../brand-library/packages/ui/src/foundations.tsx) | {children,tone='pearl',className=''}:ChildrenProps&{tone?:'white' / 'pearl' / 'navy' / 'marigold' / 'nickel'} | default, Materials | `foundations-surfaceplate--default`<br>`foundations-surfaceplate--materials` |
| OS-C004 | [DividerRule](../brand-library/packages/ui/src/foundations.tsx) | {label}: {label?:string} | default | `foundations-dividerrule--default` |
| OS-C005 | [TypeRole](../brand-library/packages/ui/src/foundations.tsx) | {children,role='body',as}:ChildrenProps&{role?:'display' / 'h2' / 'lead' / 'body' / 'support' / 'label';as?:'h1' / 'h2' / 'h3' / 'p' / 'span' / 'div'} | default, Roles | `foundations-typerole--default`<br>`foundations-typerole--roles` |
| OS-C006 | [LogoLockup](../brand-library/packages/ui/src/foundations.tsx) | {inverse=false,symbol=false}: {inverse?:boolean;symbol?:boolean} | default, Inverse, Lockup, InverseLockup | `foundations-logolockup--default`<br>`foundations-logolockup--inverse`<br>`foundations-logolockup--lockup`<br>`foundations-logolockup--inverse-lockup` |
| OS-C007 | [IconGlyph](../brand-library/packages/ui/src/foundations.tsx) | {name='arrow',size=24}: {name?:keyof typeof glyphs;size?:number} | default, Glyphs | `foundations-iconglyph--default`<br>`foundations-iconglyph--glyphs` |
| OS-C008 | [ActionButton](../brand-library/packages/ui/src/foundations.tsx) | {children=approvedCopy.cta,variant='primary',loading=false,disabled,onPointerMove,onPointerLeave,...props}:ActionButtonProps | default, States, LongLabel | `actions-actionbutton--default`<br>`actions-actionbutton--states`<br>`actions-actionbutton--long-label` |
| OS-C009 | [TextLink](../brand-library/packages/ui/src/foundations.tsx) | {children,href}:ChildrenProps&{href?:string} | default | `actions-textlink--default` |
| OS-C010 | [IconButton](../brand-library/packages/ui/src/foundations.tsx) | {label,icon='close',...props}:ButtonHTMLAttributes<HTMLButtonElement>&{label:string;icon?:keyof typeof glyphs} | default | `actions-iconbutton--default` |
| OS-C011 | [TextField](../brand-library/packages/ui/src/foundations.tsx) | {label,hint,error,id,...props}:FieldBase&InputHTMLAttributes<HTMLInputElement> | default, Error, Disabled | `forms-textfield--default`<br>`forms-textfield--error`<br>`forms-textfield--disabled` |
| OS-C012 | [TextArea](../brand-library/packages/ui/src/foundations.tsx) | {label,hint,error,id,...props}:FieldBase&TextareaHTMLAttributes<HTMLTextAreaElement> | default, Error | `forms-textarea--default`<br>`forms-textarea--error` |
| OS-C013 | [SelectField](../brand-library/packages/ui/src/foundations.tsx) | {label,options,value,onChange,disabled=false,error}:FieldBase&{options:{value:string;label:string}[];value?:string;onChange?:(value:string)=>void;disabled?:boolean} | default, Disabled | `forms-selectfield--default`<br>`forms-selectfield--disabled` |
| OS-C014 | [CheckboxField](../brand-library/packages/ui/src/foundations.tsx) | {label,...props}:{label:ReactNode}&InputHTMLAttributes<HTMLInputElement> | default, Checked | `forms-checkboxfield--default`<br>`forms-checkboxfield--checked` |
| OS-C015 | [FieldMessage](../brand-library/packages/ui/src/foundations.tsx) | {children,error=false,id}:ChildrenProps&{error?:boolean;id?:string} | default | `forms-fieldmessage--default` |
| OS-C016 | [StatusFeedback](../brand-library/packages/ui/src/foundations.tsx) | {children,status='info'}:ChildrenProps&{status?:'info' / 'success' / 'error' / 'pending'} | default, Error, Success | `forms-statusfeedback--default`<br>`forms-statusfeedback--error`<br>`forms-statusfeedback--success` |
| OS-C017 | [Disclosure](../brand-library/packages/ui/src/foundations.tsx) | {title,children,defaultOpen=false}:ChildrenProps&{title:string;defaultOpen?:boolean} | default, Expanded | `forms-disclosure--default`<br>`forms-disclosure--expanded` |
| OS-C018 | [NavigationHeader](../brand-library/packages/ui/src/foundations.tsx) | {items=[],ctaHref}:{items?:{label:string;href:string}[];ctaHref?:string} | default | `navigation-navigationheader--default` |
| OS-C019 | [NavigationFooter](../brand-library/packages/ui/src/foundations.tsx) | {items=[]}:{items?:{label:string;href:string}[]} | default | `navigation-navigationfooter--default` |
| OS-C020 | [SectionHeading](../brand-library/packages/ui/src/content.tsx) | {eyebrow,title,children}:ChildrenProps&{eyebrow?:string;title:string} | default | `content-sectionheading--default` |
| OS-C021 | [ServiceCard](../brand-library/packages/ui/src/content.tsx) | {title,number,children,steps=[]}:ChildrenProps&{title:string;number?:string;steps?:string[]} | default | `content-servicecard--default` |
| OS-C022 | [PersonCard](../brand-library/packages/ui/src/content.tsx) | {name,role,src,fictional=true}: {name:string;role:string;src?:string;fictional?:boolean} | default, MissingMedia | `content-personcard--default`<br>`content-personcard--missing-media` |
| OS-C023 | [ResourceCard](../brand-library/packages/ui/src/content.tsx) | {title,description,href,category='Field notes'}:{title:string;description:string;href?:string;category?:string} | default | `content-resourcecard--default` |
| OS-C024 | [ContactFormSpecimen](../brand-library/packages/ui/src/content.tsx) |  | default | `forms-contactformspecimen--default` |
| OS-C025 | [CentralHeroBanner](../brand-library/packages/ui/src/content.tsx) | {title=approvedCopy.hero,children=approvedCopy.vp,action,media}:BannerProps | default, MissingMedia, LongCopy | `banners-centralherobanner--default`<br>`banners-centralherobanner--missing-media`<br>`banners-centralherobanner--long-copy` |
| OS-C026 | [FullWidthSectionBanner](../brand-library/packages/ui/src/content.tsx) | {title='Your experience has a buyer-facing story.',children,action,media}:BannerProps | default | `banners-fullwidthsectionbanner--default` |
| OS-C027 | [InlineContextBanner](../brand-library/packages/ui/src/content.tsx) | {title='A useful perspective starts with a better question.',children,action}:BannerProps | default | `banners-inlinecontextbanner--default` |
| OS-C028 | [SideBanner](../brand-library/packages/ui/src/content.tsx) | {title='Keep the buyer in the room.',children,action}:BannerProps | default | `banners-sidebanner--default` |
| OS-C029 | [CTABanner](../brand-library/packages/ui/src/content.tsx) | {title='Let’s find the story worth telling.',children,action}:BannerProps | default | `banners-ctabanner--default` |
| OS-C030 | [AnnouncementBanner](../brand-library/packages/ui/src/content.tsx) | {title='A new founder field note',children,action,dismissible=true}:BannerProps&{dismissible?:boolean} | default | `banners-announcementbanner--default` |
| OS-C031 | [PublicationVideoBanner](../brand-library/packages/ui/src/content.tsx) | {title='Founder thinking. Buyer relevance.',children,media}:BannerProps | default | `banners-publicationvideobanner--default` |
| OS-C032 | [ChatLauncher](../brand-library/packages/ui/src/chat.tsx) | {onClick,expanded=false}:{onClick?:()=>void;expanded?:boolean} | default | `chat-chatlauncher--default` |
| OS-C033 | [ChatPanel](../brand-library/packages/ui/src/chat.tsx) | {initialView='open_welcome',simulateFailure=false}:{initialView?:ChatView;simulateFailure?:boolean} | default, ClosedLauncher, OpenWelcome, EmptyConversation, ActiveConversation, ComposingSending, WaitingStreaming, SuggestedActionsResources, HumanHandoff, AwayOffline, SendConnectionError, ResolvedClosed, MinimizedReopened, LongMediaMessage | `chat-chatpanel--default`<br>`chat-chatpanel--closed-launcher`<br>`chat-chatpanel--open-welcome`<br>`chat-chatpanel--empty-conversation`<br>`chat-chatpanel--active-conversation`<br>`chat-chatpanel--composing-sending`<br>`chat-chatpanel--waiting-streaming`<br>`chat-chatpanel--suggested-actions-resources`<br>`chat-chatpanel--human-handoff`<br>`chat-chatpanel--away-offline`<br>`chat-chatpanel--send-connection-error`<br>`chat-chatpanel--resolved-closed`<br>`chat-chatpanel--minimized-reopened`<br>`chat-chatpanel--long-media-message` |
| OS-C034 | [ChatMessage](../brand-library/packages/ui/src/chat.tsx) | {message}:{message:ChatEntry} | default | `chat-chatmessage--default` |
| OS-C035 | [ChatComposer](../brand-library/packages/ui/src/chat.tsx) | {value,onChange,onSend,disabled=false}:{value:string;onChange:(value:string)=>void;onSend:()=>void;disabled?:boolean} | default | `chat-chatcomposer--default` |
| OS-C036 | [ChatStatusActions](../brand-library/packages/ui/src/chat.tsx) | {state,onRetry,onResolve}:{state:'idle' / 'sending' / 'waiting' / 'error' / 'offline' / 'handoff' / 'resolved';onRetry?:()=>void;onResolve?:()=>void} | default | `chat-chatstatusactions--default` |
| OS-C037 | [SchemaNode](../brand-library/packages/ui/src/schemas.tsx) | {node,selected=false}:{node:SchemaNodeData;selected?:boolean} | default, AllRoles | `schemas-schemanode--default`<br>`schemas-schemanode--all-roles` |
| OS-C038 | [SchemaConnector](../brand-library/packages/ui/src/schemas.tsx) | {edge,sourceTitle,targetTitle}:{edge:SchemaEdge;sourceTitle:string;targetTitle:string} | default, AllRelations | `schemas-schemaconnector--default`<br>`schemas-schemaconnector--all-relations` |
| OS-C039 | [SchemaGroup](../brand-library/packages/ui/src/schemas.tsx) | {title,owner,children}:{title:string;owner?:string;children:ReactNode} | default | `schemas-schemagroup--default` |
| OS-C040 | [SchemaLegend](../brand-library/packages/ui/src/schemas.tsx) | {relations=[...relationTypes]}:{relations?:typeof relationTypes[number][]} | default | `schemas-schemalegend--default` |
| OS-C041 | [SchemaFlow](../brand-library/packages/ui/src/schemas.tsx) | {model,layout='linear_flow'}:{model:SchemaModel;layout?:typeof schemaLayouts[number]} | Default, LinearFlow, LabeledBranch, RevisionLoop, LayeredArchitecture, HumanSystemSwimlane, Comparison, LongLabels, InvalidModel | `schemas-schemaflow--default`<br>`schemas-schemaflow--linear-flow`<br>`schemas-schemaflow--labeled-branch`<br>`schemas-schemaflow--revision-loop`<br>`schemas-schemaflow--layered-architecture`<br>`schemas-schemaflow--human-system-swimlane`<br>`schemas-schemaflow--comparison`<br>`schemas-schemaflow--long-labels`<br>`schemas-schemaflow--invalid-model` |
| OS-C042 | [ProofDataCard](../brand-library/packages/ui/src/content.tsx) | {title,claim,source,status='hypothesis'}:{title:string;claim:string;source?:{label:string;href:string};status?:'fact' / 'interpretation' / 'hypothesis' / 'gap'} | default | `editorial-proofdatacard--default` |
| OS-C043 | [EditorialLabel](../brand-library/packages/ui/src/content.tsx) | {children}:ChildrenProps | default | `editorial-editoriallabel--default` |
| OS-C044 | [QuoteAttribution](../brand-library/packages/ui/src/content.tsx) | {quote,name,role,fictional=true}:{quote:string;name:string;role?:string;fictional?:boolean} | default | `editorial-quoteattribution--default` |
| OS-C045 | [ChecklistSteps](../brand-library/packages/ui/src/content.tsx) | {items,current=0}:{items:string[];current?:number} | default | `editorial-checkliststeps--default` |
| OS-C046 | [ComparisonGrid](../brand-library/packages/ui/src/content.tsx) | {headers,rows}:{headers:[string,string,string];rows:[string,string,string][]} | default | `editorial-comparisongrid--default` |
| OS-C047 | [SourceFootnote](../brand-library/packages/ui/src/content.tsx) | {label,href,number=1}:{label:string;href?:string;number?:number} | default | `editorial-sourcefootnote--default` |
| OS-C048 | [NativePostFrame](../brand-library/packages/ui/src/content.tsx) | {author='Maya Reed',role='Fictional founder · B2B AI SaaS',children,artwork}:ChildrenProps&{author?:string;role?:string;artwork?:ReactNode} | default | `editorial-nativepostframe--default` |
| OS-C049 | [MediaShellMask](../brand-library/packages/ui/src/content.tsx) | {src,alt,ratio='landscape',children}:ChildrenProps&{src?:string;alt:string;ratio?:'landscape' / 'portrait' / 'square'} | default, BrokenMedia | `editorial-mediashellmask--default`<br>`editorial-mediashellmask--broken-media` |
| OS-C050 | [MetricWithSource](../brand-library/packages/ui/src/content.tsx) | {value,label,source,qualifier=''}:{value:string;label:string;source:{label:string;href?:string};qualifier?:string} | default | `editorial-metricwithsource--default` |
| OS-C051 | [PaginationSeries](../brand-library/packages/ui/src/content.tsx) | {page,total,onChange}:{page:number;total:number;onChange?:(page:number)=>void} | default | `editorial-paginationseries--default` |
| OS-C052 | [DemoFeedbackCard](../brand-library/packages/ui/src/content.tsx) | {kind='email',name='Alex Morgan',children='The interview helped me see the idea I wanted to explain.'}:ChildrenProps&{kind?:'email' / 'comment';name?:string} | default, Comment, LongText | `editorial-demofeedbackcard--default`<br>`editorial-demofeedbackcard--comment`<br>`editorial-demofeedbackcard--long-text` |
| OS-C053 | [OpeningTitle](../brand-library/packages/ui/src/content.tsx) | {eyebrow='Founder perspective',title='The customer problem behind the product.'}:{eyebrow?:string;title?:string} | default | `video-openingtitle--default` |
| OS-C054 | [LowerThird](../brand-library/packages/ui/src/content.tsx) | {name='Maya Reed',role='Fictional founder · design specimen'}:{name?:string;role?:string} | default | `video-lowerthird--default` |
| OS-C055 | [Captions](../brand-library/packages/ui/src/content.tsx) | {text,activeWord}:{text:string;activeWord?:string} | default | `video-captions--default` |
| OS-C056 | [EmphasisWordNumber](../brand-library/packages/ui/src/content.tsx) | {children,variant='highlight'}:ChildrenProps&{variant?:'highlight' / 'underline' / 'number'} | default, Variants | `video-emphasiswordnumber--default`<br>`video-emphasiswordnumber--variants` |
| OS-C057 | [CitationOverlay](../brand-library/packages/ui/src/content.tsx) | {label,href}:{label:string;href?:string} | default | `video-citationoverlay--default` |
| OS-C058 | [ChapterDivider](../brand-library/packages/ui/src/content.tsx) | {number='01',title}:{number?:string;title:string} | default | `video-chapterdivider--default` |
| OS-C059 | [ClosingCTA](../brand-library/packages/ui/src/content.tsx) | {title=approvedCopy.hero,href}:{title?:string;href?:string} | default | `video-closingcta--default` |
| OS-C060 | [WatermarkSignature](../brand-library/packages/ui/src/content.tsx) | {inverse=false}:{inverse?:boolean} | default | `video-watermarksignature--default` |
| OS-C061 | [PresenterMediaScene](../brand-library/packages/ui/src/content.tsx) | {src,name='Maya Reed',caption='Make the customer problem clear.'}:{src?:string;name?:string;caption?:string} | default | `scenes-presentermediascene--default` |
| OS-C062 | [ObjectProcessScene](../brand-library/packages/ui/src/content.tsx) | {steps=['Interview','Strategy','Drafts','Founder approval']}: {steps?:string[]} | default | `scenes-objectprocessscene--default` |
| OS-C063 | [EvidenceComparisonScene](../brand-library/packages/ui/src/content.tsx) |  | default | `scenes-evidencecomparisonscene--default` |
| OS-C064 | [ClosingScene](../brand-library/packages/ui/src/content.tsx) | {href}:{href?:string} | default | `scenes-closingscene--default` |

## Live experience primitives and website assemblies

| Component | Supported options / relationship | Stories |
| --- | --- | --- |
| ThreeTiltButton | Actual3D decorative plate with a semantic DOM button. See complete API/matrices above. | V4 button catalog; V3 Perspective media / Buttons |
| PerspectiveVideo | poster,src,title,description,caption,className,onOpenChange; tilt:left/right; autoPlayOnOpen(defaultfalse). Shared16:9 plate, accessible dialog. | experience-v3-perspective-media--left-plate; --right-plate |
| NeuronField | imageSrc; progress:MotionValue<number>; staticOnly; modelSrc. Real cortical mesh, five projected semantic anchors, camera orbit/pin/recede. Static/reduced retains all labels. | experience-v3-founder-constellation--full-field; --static; --progress |

Website assemblies are separate consumers of the shared primitives; they are not additional OS-C registry families.

| Assembly | Story / source |
| --- | --- |
| AtmosphereHero | `v3-website-blocks--hero` |
| ExpertiseChapter | `v3-website-blocks--expertise` |
| PublicationStack | `v3-website-blocks--publications` |
| ServiceStack | `v3-website-blocks--services` |
| PricePlans | `v3-website-blocks--pricing` |
| CustomerOpinion | `v3-website-blocks--emails` |
| ProcessRail | `v3-website-blocks--process` |
| ClosingPanel | `v3-website-blocks--closing` |
| PostCard | [Used inside publication stack; no standalone story](../brand-library/website-v3/App.tsx) |
| RevealHeading | `v3-website-blocks--heading` |
| SoundWaves | `v3-website-blocks--resonance` |

## All88 native editable catalog layouts

The dimensions are export canvases, not CSS viewport sizes. Every category has eleven actual SVG masters and rendered PNGs. `CatalogSurface` accepts `id`, `slots`, `titleLines`, `bodyLines`, `eyebrow`, `caption`, `mediaSrc`, `className`, `ariaLabel`, and `style`. Replace known slots. Keep source line counts, spacing and declared angle; review new copy at actual size. Static video frames do not play video by themselves.

[88-entry manifest](../brand-library/packages/catalog-v3/manifest.json) · [renderer and category adapters](../brand-library/packages/catalog-v3/CatalogSurface.tsx)

### banner — eleven variants

Story: `outspoken-v3-editable-catalog--banners`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/banner.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-BA3-01](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-01.svg) | buyer-question / split-field | 1584×396 | media, eyebrow, title-0, title-1, body-0 |
| [OS-BA3-02](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-02.svg) | experience / center-sign | 1584×396 | eyebrow, title-0, body-0 |
| [OS-BA3-03](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-03.svg) | position / margin-rail | 1584×396 | eyebrow, title-0, body-0 |
| [OS-BA3-04](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-04.svg) | sequence / numbered-editorial | 1584×396 | eyebrow, title-0, body-0 |
| [OS-BA3-05](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-05.svg) | decision / horizon-band | 1584×396 | media, eyebrow, title-0, body-0 |
| [OS-BA3-06](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-06.svg) | voice / photo-column | 1584×396 | media, eyebrow, title-0, body-0 |
| [OS-BA3-07](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-07.svg) | change / ribbon-sign | 1584×396 | eyebrow, title-0, body-0 |
| [OS-BA3-08](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-08.svg) | evidence / quote-field | 1584×396 | eyebrow, title-0, body-0 |
| [OS-BA3-09](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-09.svg) | next-step / open-ledger | 1584×396 | eyebrow, title-0, body-0 |
| [OS-BA3-10](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-10.svg) | questions / stepped-argument | 1584×396 | eyebrow, title-0, body-0 |
| [OS-BA3-11](../brand-library/packages/catalog-v3/masters/banner/OS-BA3-11.svg) | approval / diagonal-marker | 1584×396 | eyebrow, title-0, body-0 |
### poster — eleven variants

Story: `outspoken-v3-editable-catalog--posters`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/poster.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-PO3-01](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-01.svg) | buyer-question / split-field | 1080×1350 | media, eyebrow, title-0, title-1, title-2, title-3, body-0, body-1 |
| [OS-PO3-02](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-02.svg) | experience / center-sign | 1080×1350 | eyebrow, title-0, title-1, title-2, body-0, media |
| [OS-PO3-03](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-03.svg) | position / margin-rail | 1080×1350 | media, eyebrow, title-0, title-1, title-2, title-3, body-0 |
| [OS-PO3-04](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-04.svg) | sequence / numbered-editorial | 1080×1350 | eyebrow, title-0, title-1, title-2, body-0, media |
| [OS-PO3-05](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-05.svg) | decision / horizon-band | 1080×1350 | media, eyebrow, title-0, title-1, body-0 |
| [OS-PO3-06](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-06.svg) | voice / photo-column | 1080×1350 | media, eyebrow, title-0, title-1, title-2, title-3, body-0, body-1 |
| [OS-PO3-07](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-07.svg) | change / ribbon-sign | 1080×1350 | eyebrow, title-0, title-1, body-0, media, media, media |
| [OS-PO3-08](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-08.svg) | evidence / quote-field | 1080×1350 | media, eyebrow, title-0, title-1, title-2, body-0, body-1, caption |
| [OS-PO3-09](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-09.svg) | next-step / open-ledger | 1080×1350 | eyebrow, title-0, title-1, title-2, body-0, body-1, media |
| [OS-PO3-10](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-10.svg) | questions / stepped-argument | 1080×1350 | eyebrow, title-0, title-1, body-0, body-1, media |
| [OS-PO3-11](../brand-library/packages/catalog-v3/masters/poster/OS-PO3-11.svg) | approval / diagonal-marker | 1080×1350 | eyebrow, title-0, title-1, body-0, body-1, check-0, check-1, check-2 |
### block — eleven variants

Story: `outspoken-v3-editable-catalog--blocks`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/block.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-BL3-01](../brand-library/packages/catalog-v3/masters/block/OS-BL3-01.svg) | buyer-question / split-field | 1200×660 | media, eyebrow, title-0, title-1, body-0, body-1 |
| [OS-BL3-02](../brand-library/packages/catalog-v3/masters/block/OS-BL3-02.svg) | experience / center-sign | 1200×660 | eyebrow, title-0, title-1, body-0 |
| [OS-BL3-03](../brand-library/packages/catalog-v3/masters/block/OS-BL3-03.svg) | position / margin-rail | 1200×660 | eyebrow, title-0, title-1, body-0 |
| [OS-BL3-04](../brand-library/packages/catalog-v3/masters/block/OS-BL3-04.svg) | sequence / numbered-editorial | 1200×660 | eyebrow, title-0, title-1, body-0 |
| [OS-BL3-05](../brand-library/packages/catalog-v3/masters/block/OS-BL3-05.svg) | decision / horizon-band | 1200×660 | media, eyebrow, title-0, body-0 |
| [OS-BL3-06](../brand-library/packages/catalog-v3/masters/block/OS-BL3-06.svg) | voice / photo-column | 1200×660 | media, eyebrow, title-0, title-1, body-0, body-1 |
| [OS-BL3-07](../brand-library/packages/catalog-v3/masters/block/OS-BL3-07.svg) | change / ribbon-sign | 1200×660 | eyebrow, title-0, body-0 |
| [OS-BL3-08](../brand-library/packages/catalog-v3/masters/block/OS-BL3-08.svg) | evidence / quote-field | 1200×660 | eyebrow, title-0, title-1, body-0 |
| [OS-BL3-09](../brand-library/packages/catalog-v3/masters/block/OS-BL3-09.svg) | next-step / open-ledger | 1200×660 | eyebrow, title-0, title-1, body-0, body-1 |
| [OS-BL3-10](../brand-library/packages/catalog-v3/masters/block/OS-BL3-10.svg) | questions / stepped-argument | 1200×660 | eyebrow, title-0, title-1, body-0 |
| [OS-BL3-11](../brand-library/packages/catalog-v3/masters/block/OS-BL3-11.svg) | approval / diagonal-marker | 1200×660 | eyebrow, title-0, title-1, body-0 |
### heading — eleven variants

Story: `outspoken-v3-editable-catalog--headings`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/heading.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-HE3-01](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-01.svg) | buyer-question / split-field | 1200×360 | media, eyebrow, title-0, title-1, body-0 |
| [OS-HE3-02](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-02.svg) | experience / center-sign | 1200×360 | eyebrow, title-0, body-0 |
| [OS-HE3-03](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-03.svg) | position / margin-rail | 1200×360 | eyebrow, title-0, title-1, body-0 |
| [OS-HE3-04](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-04.svg) | sequence / numbered-editorial | 1200×360 | eyebrow, title-0, body-0 |
| [OS-HE3-05](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-05.svg) | decision / horizon-band | 1200×360 | media, eyebrow, title-0, body-0 |
| [OS-HE3-06](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-06.svg) | voice / photo-column | 1200×360 | media, eyebrow, title-0, body-0 |
| [OS-HE3-07](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-07.svg) | change / ribbon-sign | 1200×360 | eyebrow, title-0, body-0 |
| [OS-HE3-08](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-08.svg) | evidence / quote-field | 1200×360 | eyebrow, title-0, body-0 |
| [OS-HE3-09](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-09.svg) | next-step / open-ledger | 1200×360 | eyebrow, title-0, body-0 |
| [OS-HE3-10](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-10.svg) | questions / stepped-argument | 1200×360 | eyebrow, title-0, body-0 |
| [OS-HE3-11](../brand-library/packages/catalog-v3/masters/heading/OS-HE3-11.svg) | approval / diagonal-marker | 1200×360 | eyebrow, title-0, body-0 |
### video-frame — eleven variants

Story: `outspoken-v3-editable-catalog--video-frames`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/video-frame.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-VF3-01](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-01.svg) | buyer-question / video-frame-buyer-question | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-02](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-02.svg) | experience / video-frame-experience | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-03](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-03.svg) | position / video-frame-position | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-04](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-04.svg) | sequence / video-frame-sequence | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-05](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-05.svg) | decision / video-frame-decision | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-06](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-06.svg) | voice / video-frame-voice | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-07](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-07.svg) | change / video-frame-change | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-08](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-08.svg) | evidence / video-frame-evidence | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-09](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-09.svg) | next-step / video-frame-next-step | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-10](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-10.svg) | questions / video-frame-questions | 1600×900 | eyebrow, media, caption, title-0 |
| [OS-VF3-11](../brand-library/packages/catalog-v3/masters/video-frame/OS-VF3-11.svg) | approval / video-frame-approval | 1600×900 | eyebrow, media, caption, title-0 |
### caption-emphasis — eleven variants

Story: `outspoken-v3-editable-catalog--captions-and-emphasis`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/caption-emphasis.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-CE3-01](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-01.svg) | buyer-question / caption-emphasis-buyer-question | 1200×360 | title-0, body-0 |
| [OS-CE3-02](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-02.svg) | experience / caption-emphasis-experience | 1200×360 | title-0, body-0 |
| [OS-CE3-03](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-03.svg) | position / caption-emphasis-position | 1200×360 | title-0, body-0 |
| [OS-CE3-04](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-04.svg) | sequence / caption-emphasis-sequence | 1200×360 | title-0, body-0 |
| [OS-CE3-05](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-05.svg) | decision / caption-emphasis-decision | 1200×360 | title-0, body-0 |
| [OS-CE3-06](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-06.svg) | voice / caption-emphasis-voice | 1200×360 | title-0, body-0 |
| [OS-CE3-07](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-07.svg) | change / caption-emphasis-change | 1200×360 | title-0, body-0 |
| [OS-CE3-08](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-08.svg) | evidence / caption-emphasis-evidence | 1200×360 | title-0, body-0 |
| [OS-CE3-09](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-09.svg) | next-step / caption-emphasis-next-step | 1200×360 | title-0, body-0 |
| [OS-CE3-10](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-10.svg) | questions / caption-emphasis-questions | 1200×360 | title-0, body-0 |
| [OS-CE3-11](../brand-library/packages/catalog-v3/masters/caption-emphasis/OS-CE3-11.svg) | approval / caption-emphasis-approval | 1200×360 | title-0, body-0 |
### schema — eleven variants

Story: `outspoken-v3-editable-catalog--schemas`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/schema.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-SC3-01](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-01.svg) | buyer-question / schema-buyer-question | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0, node-2-1 |
| [OS-SC3-02](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-02.svg) | experience / schema-experience | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0, node-2-1 |
| [OS-SC3-03](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-03.svg) | position / schema-position | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0, node-3-0 |
| [OS-SC3-04](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-04.svg) | sequence / schema-sequence | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0, node-3-0, node-4-0, node-4-1 |
| [OS-SC3-05](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-05.svg) | decision / schema-decision | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-1-1, node-2-0, node-3-0 |
| [OS-SC3-06](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-06.svg) | voice / schema-voice | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-1-1, node-2-0, node-3-0 |
| [OS-SC3-07](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-07.svg) | change / schema-change | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0, node-3-0 |
| [OS-SC3-08](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-08.svg) | evidence / schema-evidence | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0 |
| [OS-SC3-09](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-09.svg) | next-step / schema-next-step | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-1-1, node-2-0, node-2-1 |
| [OS-SC3-10](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-10.svg) | questions / schema-questions | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0, node-3-0, node-3-1 |
| [OS-SC3-11](../brand-library/packages/catalog-v3/masters/schema/OS-SC3-11.svg) | approval / schema-approval | 1200×900 | eyebrow, title-0, body-0, node-0-0, node-1-0, node-2-0, node-3-0 |
### publication — eleven variants

Story: `outspoken-v3-editable-catalog--publications`. [all-eleven contact sheet](../brand-library/packages/catalog-v3/contact-sheets/publication.png)

| ID / native source | Variant / layout | Canvas | Editable slots |
| --- | --- | --- | --- |
| [OS-PUB3-01](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-01.svg) | OS-T301 / existing-native-master-OS-T301 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12 |
| [OS-PUB3-02](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-02.svg) | OS-T302 / existing-native-master-OS-T302 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12, text-13, text-14 |
| [OS-PUB3-03](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-03.svg) | OS-T303 / existing-native-master-OS-T303 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12 |
| [OS-PUB3-04](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-04.svg) | OS-T304-01 / existing-native-master-OS-T304-01 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9 |
| [OS-PUB3-05](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-05.svg) | OS-T305 / existing-native-master-OS-T305 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12, text-13, text-14, text-15 |
| [OS-PUB3-06](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-06.svg) | OS-T306 / existing-native-master-OS-T306 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12, text-13, text-14, text-15, text-16 |
| [OS-PUB3-07](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-07.svg) | OS-T307 / existing-native-master-OS-T307 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12, text-13, text-14, text-15, text-16, text-17 |
| [OS-PUB3-08](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-08.svg) | OS-T308 / existing-native-master-OS-T308 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12 |
| [OS-PUB3-09](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-09.svg) | OS-T309 / existing-native-master-OS-T309 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9, text-10, text-11, text-12, text-13, text-14, text-15, text-16 |
| [OS-PUB3-10](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-10.svg) | OS-T310 / existing-native-master-OS-T310 | 1080×1350 | text-0, text-1, text-2, text-3, text-4, text-5, text-6, text-7, text-8, text-9 |
| [OS-PUB3-11](../brand-library/packages/catalog-v3/masters/publication/OS-PUB3-11.svg) | approval-checklist / open-review-checklist | 1080×1350 | eyebrow, title-0, title-1, body-0, check-0, check-1, check-2, check-3, check-4 |

### Video-frame use and runtime aspect options

The eleven OS-VF3 layouts above are the complete video-frame category, already included in88. Each has a1600×900 canvas,54px outer margin,30px media safe zone,12px minimum text gap, native rest yaw0°, and optional website yaw12°→0° focus. Their topics are buyer question, experience, position, sequence, decision, voice, change, evidence, next step, questions and checklist. Use each manifest entry’s exact defaults and slots.

Additional frame APIs are different things: `MediaShellMask` supports `landscape`(16:10), `portrait`(4:5), and `square`(1:1), with an explicit missing/broken media fallback. `PerspectiveVideo` is16:9 with left/right rest angles. The scene export system recomposes landscape,square,portrait; changing a frame is not proof of a recomposed film. Caption,title,lower-third,citation,chapter,closing and watermark overlays are OS-C053…060 in the64-family table.

## All25 subject objects

Use the GLB for real camera changes; use transparent PNG/WebP for artwork. Each family also has a separately editable native SVG glyph and metadata. The25 small glyphs are not counted as25 more subject objects.

| ID / name | Context | Variants / files |
| --- | --- | --- |
| OS-O301 · Microphone | Interview and founder voice | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O301.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O301.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O301.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O301.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O301.json) |
| OS-O302 · Wavefront | A point of view travelling outward | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O302.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O302.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O302.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O302.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O302.json) |
| OS-O303 · Megaphone | Distribution and campaign amplification | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O303.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O303.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O303.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O303.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O303.json) |
| OS-O304 · Ink pen | Professional writing and editorial judgment | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O304.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O304.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O304.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O304.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O304.json) |
| OS-O305 · Notebook | First-hand experience and source notes | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O305.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O305.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O305.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O305.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O305.json) |
| OS-O306 · Publication stack | One idea across several formats | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O306.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O306.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O306.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O306.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O306.json) |
| OS-O307 · Search lens | Buyer language and discoverability | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O307.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O307.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O307.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O307.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O307.json) |
| OS-O308 · Profile frame | A recognizable founder presence | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O308.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O308.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O308.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O308.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O308.json) |
| OS-O309 · Dialogue | An exchange that clarifies the idea | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O309.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O309.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O309.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O309.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O309.json) |
| OS-O310 · Envelope | A useful follow-up | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O310.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O310.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O310.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O310.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O310.json) |
| OS-O311 · Calendar | A considered publishing rhythm | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O311.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O311.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O311.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O311.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O311.json) |
| OS-O312 · Evidence check | A claim checked against its source | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O312.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O312.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O312.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O312.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O312.json) |
| OS-O313 · Compass | A deliberate position | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O313.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O313.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O313.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O313.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O313.json) |
| OS-O314 · Network | The relevant buying group | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O314.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O314.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O314.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O314.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O314.json) |
| OS-O315 · Spotlight | Attention on the right point | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O315.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O315.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O315.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O315.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O315.json) |
| OS-O316 · Play frame | A story in motion | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O316.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O316.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O316.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O316.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O316.json) |
| OS-O317 · Camera | A believable human presence | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O317.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O317.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O317.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O317.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O317.json) |
| OS-O318 · Architecture bridge | Connect expertise to buyer value | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O318.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O318.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O318.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O318.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O318.json) |
| OS-O319 · Target | A specific buyer problem | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O319.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O319.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O319.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O319.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O319.json) |
| OS-O320 · Ripple | A useful idea resonates | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O320.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O320.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O320.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O320.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O320.json) |
| OS-O321 · Signal bars | A clearer signal | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O321.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O321.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O321.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O321.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O321.json) |
| OS-O322 · Content folder | An organized editorial handoff | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O322.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O322.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O322.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O322.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O322.json) |
| OS-O323 · Bookmark | An idea worth keeping | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O323.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O323.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O323.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O323.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O323.json) |
| OS-O324 · Story reel | Sequence and narrative | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O324.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O324.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O324.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O324.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O324.json) |
| OS-O325 · Quote | The founder’s own words | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-O325.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-O325.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-O325.webp) · [native SVG](../brand-library/packages/assets/revisions/v3/objects/OS-O325.svg) · [recipe/metadata](../brand-library/packages/assets/revisions/v3/objects/OS-O325.json) |

## All11 word sculptures

These physical signs use their own geometry and outlined counterpart. They supplement editable text; they are not interchangeable logo lockups. The current OUTSPOKEN brand sign must retain uppercase geometry and its final refreshed hash.

| ID | Word | Variants / files |
| --- | --- | --- |
| OS-W301 | Voice | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W301.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W301.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W301.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W301.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W301.json) |
| OS-W302 | Story | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W302.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W302.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W302.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W302.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W302.json) |
| OS-W303 | Signal | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W303.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W303.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W303.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W303.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W303.json) |
| OS-W304 | Proof | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W304.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W304.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W304.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W304.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W304.json) |
| OS-W305 | Trust | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W305.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W305.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W305.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W305.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W305.json) |
| OS-W306 | Clarity | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W306.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W306.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W306.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W306.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W306.json) |
| OS-W307 | Context | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W307.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W307.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W307.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W307.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W307.json) |
| OS-W308 | Product | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W308.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W308.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W308.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W308.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W308.json) |
| OS-W309 | Perspective | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W309.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W309.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W309.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W309.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W309.json) |
| OS-W310 | Conversation | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W310.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W310.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W310.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W310.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W310.json) |
| OS-W311 | OUTSPOKEN | [GLB](../brand-library/packages/assets/revisions/v3/objects/OS-W311.glb) · [PNG](../brand-library/packages/assets/revisions/v3/objects/OS-W311.png) · [WebP](../brand-library/packages/assets/revisions/v3/objects/OS-W311.webp) · [outlined SVG](../brand-library/packages/assets/revisions/v3/objects/OS-W311.svg) · [metadata](../brand-library/packages/assets/revisions/v3/objects/OS-W311.json) |

## Fourteen publication exports, ten master families

Standalone editable sources have uppercase OUT/SPOKEN footer lettering. OS-T304 has five slides; the other nine families each have one export. These are original illustrative examples, not published client content.

| ID | Format / title | Source |
| --- | --- | --- |
| OS-T301 | professional text / Before the opening line | [native SVG](../brand-library/packages/content/revisions/v3/OS-T301.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T301.png) |
| OS-T302 | personal story / The moment your view changed | [native SVG](../brand-library/packages/content/revisions/v3/OS-T302.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T302.png) |
| OS-T303 | founder perspective / The feature you chose not to build | [native SVG](../brand-library/packages/content/revisions/v3/OS-T303.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T303.png) |
| OS-T304-01 | carousel slide / Product judgment / 01 | [native SVG](../brand-library/packages/content/revisions/v3/OS-T304-01.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T304-01.png) |
| OS-T305 | interface walkthrough / A draft is not an approved post | [native SVG](../brand-library/packages/content/revisions/v3/OS-T305.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T305.png) |
| OS-T306 | architecture schema / Automate the steps, keep the judgment | [native SVG](../brand-library/packages/content/revisions/v3/OS-T306.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T306.png) |
| OS-T307 | comparison / A promise needs something specific | [native SVG](../brand-library/packages/content/revisions/v3/OS-T307.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T307.png) |
| OS-T308 | company launch / Start the launch with the customer | [native SVG](../brand-library/packages/content/revisions/v3/OS-T308.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T308.png) |
| OS-T309 | evidence note / Make the basis of the claim visible | [native SVG](../brand-library/packages/content/revisions/v3/OS-T309.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T309.png) |
| OS-T310 | video story / One decision, your explanation | [native SVG](../brand-library/packages/content/revisions/v3/OS-T310.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T310.png) |
| OS-T304-02 | carousel slide / Product judgment / 02 | [native SVG](../brand-library/packages/content/revisions/v3/OS-T304-02.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T304-02.png) |
| OS-T304-03 | carousel slide / Product judgment / 03 | [native SVG](../brand-library/packages/content/revisions/v3/OS-T304-03.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T304-03.png) |
| OS-T304-04 | carousel slide / Product judgment / 04 | [native SVG](../brand-library/packages/content/revisions/v3/OS-T304-04.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T304-04.png) |
| OS-T304-05 | carousel slide / Product judgment / 05 | [native SVG](../brand-library/packages/content/revisions/v3/OS-T304-05.svg) · [rendered PNG](../brand-library/packages/content/revisions/v3/OS-T304-05.png) |

## Reuse and verification

Keep text editable and illustrative labels visible. Preserve protected agency wording. Do not invent unsupported sizes,variants,client proof,account operations or runtime readiness. A static SVG, native Figma component, React story, GLB and PNG are different representations. Inspect the representation you actually changed.

The current identity manifest and final source hashes override old logo thumbnails. Local-only delivery; no public deployment is requested. Full V4 integration, source-hash freeze and owner artistic acceptance remain separate gates.


## Final runtime and packaging boundary

The current 57-page book/PDF was regenerated for the owner’s solid-silver primary 2D correction. All 203 input hashes match current source, including the earlier PerspectiveVideo focus repair. The previous PDF, source map and amendment are preserved under `[dated-local-evidence-omitted]`. Current book checks passed 21/21; all 57 rendered page bounds and 186 images passed. The refreshed five critical PDF pages passed independent review. See the [solid-primary book recapture]([dated-local-evidence-omitted]).

Portable packaging is verified separately by `[dated-local-evidence-omitted]` and the delivered `DELIVERY-MANIFEST.json`/`FILE-CHECKSUMS.json`. Canonical records verify implementation and remain frozen before packaging; no archive PASS or future ZIP hash is inferred here.


The current primary 2D wordmark uses navy OUT and full solid Nickel silver SPOKEN (`#A9AFBA`), with no horizontal glint or color transition. Existing `*-gradient.svg` filenames remain compatibility paths. Natural reflections remain valid in the separate 3D artwork and unchanged preserved reference studies.
