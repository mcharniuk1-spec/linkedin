import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import * as C from '../src';
function ComposerDemo(){const [value,setValue]=useState('');return <C.ChatComposer value={value} onChange={setValue} onSend={()=>setValue('')}/>};
function PaginationDemo(){const [page,setPage]=useState(1);return <C.PaginationSeries page={page} total={5} onChange={setPage}/>};
const meta={title:'Content/SectionHeading',component:C.SectionHeading,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C020 · canonical shared module. Stage 1 candidate; Figma and owner acceptance are separate.'}}}} satisfies Meta<typeof C.SectionHeading>;
export default meta;
type Story = StoryObj;
export const Default:Story={render:()=>(<C.SectionHeading eyebrow="A point of view worth sharing" title="Your experience has something useful to say.">Connect founder judgment to a buyer question.</C.SectionHeading>)};
