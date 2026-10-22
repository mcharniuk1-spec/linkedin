import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import * as C from '../src';
function ComposerDemo(){const [value,setValue]=useState('');return <C.ChatComposer value={value} onChange={setValue} onSend={()=>setValue('')}/>};
function PaginationDemo(){const [page,setPage]=useState(1);return <C.PaginationSeries page={page} total={5} onChange={setPage}/>};
const meta={title:'Banners/AnnouncementBanner',component:C.AnnouncementBanner,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C030 · canonical shared module. Stage 1 candidate; Figma and owner acceptance are separate.'}}}} satisfies Meta<typeof C.AnnouncementBanner>;
export default meta;
type Story = StoryObj;
export const Default:Story={render:()=>(<C.AnnouncementBanner>Read the latest editorial specimen.</C.AnnouncementBanner>)};
