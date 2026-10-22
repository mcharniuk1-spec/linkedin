import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import * as C from '../src';
function ComposerDemo(){const [value,setValue]=useState('');return <C.ChatComposer value={value} onChange={setValue} onSend={()=>setValue('')}/>};
function PaginationDemo(){const [page,setPage]=useState(1);return <C.PaginationSeries page={page} total={5} onChange={setPage}/>};
const meta={title:'Content/ServiceCard',component:C.ServiceCard,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C021 · canonical shared module. Stage 1 candidate; Figma and owner acceptance are separate.'}}}} satisfies Meta<typeof C.ServiceCard>;
export default meta;
type Story = StoryObj;
export const Default:Story={render:()=>(<C.ServiceCard title="Clarify the story" steps={["Interview","Buyer relevance","Positioning"]}><p>Make the founder’s experience clear and useful.</p></C.ServiceCard>)};
