import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import * as C from '../src';
function ComposerDemo(){const [value,setValue]=useState('');return <C.ChatComposer value={value} onChange={setValue} onSend={()=>setValue('')}/>};
function PaginationDemo(){const [page,setPage]=useState(1);return <C.PaginationSeries page={page} total={5} onChange={setPage}/>};
const meta={title:'Foundations/StackGrid',component:C.StackGrid,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C002 · canonical shared module. Stage 1 candidate; Figma and owner acceptance are separate.'}}}} satisfies Meta<typeof C.StackGrid>;
export default meta;
type Story = StoryObj;
export const Default:Story={render:()=>(<C.StackGrid columns={3}>{["Experience","Judgment","Buyer relevance"].map(x=><C.SurfacePlate key={x}><h3>{x}</h3><p>One useful idea, with room to read.</p></C.SurfacePlate>)}</C.StackGrid>)};
