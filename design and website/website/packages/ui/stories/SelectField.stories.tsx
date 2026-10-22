import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import * as C from '../src';
function ComposerDemo(){const [value,setValue]=useState('');return <C.ChatComposer value={value} onChange={setValue} onSend={()=>setValue('')}/>};
function PaginationDemo(){const [page,setPage]=useState(1);return <C.PaginationSeries page={page} total={5} onChange={setPage}/>};
const meta={title:'Forms/SelectField',component:C.SelectField,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C013 · canonical shared module. Stage 1 candidate; Figma and owner acceptance are separate.'}}}} satisfies Meta<typeof C.SelectField>;
export default meta;
type Story = StoryObj;
export const Default:Story={render:()=>(<C.SelectField label="Your focus" options={[{value:"positioning",label:"Positioning"},{value:"content",label:"Founder content"}]}/>)};
export const Disabled:Story={render:()=>(<C.SelectField label="Focus" disabled options={[{value:"x",label:"Unavailable"}]}/>)};

export const WithHint:Story={render:()=>(<C.SelectField label="Your focus" hint="Choose the first area to discuss." options={[{value:"positioning",label:"Positioning"},{value:"content",label:"Founder content"}]}/>)};
export const WithError:Story={render:()=>(<C.SelectField label="Your focus" hint="Choose the first area to discuss." error="Choose a focus before continuing." options={[{value:"",label:"Choose an area"},{value:"content",label:"Founder content"}]}/>)};
