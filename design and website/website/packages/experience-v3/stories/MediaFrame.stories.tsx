import type {Meta,StoryObj} from '@storybook/react-vite';
import {MediaFrame} from '../frames/MediaFrame';
const poster='/assets/revisions/v5/people/founder-blue.webp';
const meta={title:'Experience V10/Media frame',parameters:{layout:'centered'},tags:['autodocs']} satisfies Meta;export default meta;type Story=StoryObj<typeof meta>;
export const Hairline:Story={render:()=> <div style={{width:560}}><MediaFrame variant="hairline" caption="Illustrative interview image"><img src={poster} alt="Fictional founder interview image"/></MediaFrame></div>};
export const Bracket:Story={render:()=> <div style={{width:560,padding:12}}><MediaFrame variant="bracket" caption="Illustrative interview image"><img src={poster} alt="Fictional founder interview image"/></MediaFrame></div>};
export const Square:Story={render:()=> <div style={{width:360}}><MediaFrame variant="hairline" ratio="1 / 1"><img src={poster} alt="Fictional founder interview image"/></MediaFrame></div>};
