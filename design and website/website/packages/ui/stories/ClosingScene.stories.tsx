import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import * as C from '../src';
function ComposerDemo(){const [value,setValue]=useState('');return <C.ChatComposer value={value} onChange={setValue} onSend={()=>setValue('')}/>};
function PaginationDemo(){const [page,setPage]=useState(1);return <C.PaginationSeries page={page} total={5} onChange={setPage}/>};
const meta={title:'Scenes/ClosingScene',component:C.ClosingScene,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C064 · canonical shared module. Stage 1 candidate; Figma and owner acceptance are separate.'}}}} satisfies Meta<typeof C.ClosingScene>;
export default meta;
type Story = StoryObj;
export const Default:Story={render:()=>(<C.ClosingScene/>)};
