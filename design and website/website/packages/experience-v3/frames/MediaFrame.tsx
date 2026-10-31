import type {CSSProperties,ReactNode} from 'react';
import './media-frame.css';

/** OS-FRAME-V10. Two finished frames with exact corner geometry: inner radius = outer radius - mat, brackets sit on the media corners. */
export type MediaFrameProps={variant?:'hairline'|'bracket';children:ReactNode;caption?:string;ratio?:string;label?:string};
export function MediaFrame({variant='hairline',children,caption,ratio='16 / 10',label}:MediaFrameProps){
  return <figure className={'os-frame os-frame--'+variant} style={{'--ratio':ratio} as CSSProperties} aria-label={label}>
    <div className="os-frame__media">{children}</div>
    {caption?<figcaption>{caption}</figcaption>:null}
  </figure>;
}
