import type { Meta, StoryObj } from '@storybook/react-vite';
import { useState } from 'react';
import * as C from '../src';
function ComposerDemo(){const [value,setValue]=useState('');return <C.ChatComposer value={value} onChange={setValue} onSend={()=>setValue('')}/>};
function PaginationDemo(){const [page,setPage]=useState(1);return <C.PaginationSeries page={page} total={5} onChange={setPage}/>};
const meta={title:'Editorial/ComparisonGrid',component:C.ComparisonGrid,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C046 · canonical shared module. Stage 1 candidate; Figma and owner acceptance are separate.'}}}} satisfies Meta<typeof C.ComparisonGrid>;
export default meta;
type Story = StoryObj;
export const Default:Story={render:()=>(<C.ComparisonGrid headers={["Question","Claim","Source-led wording"]} rows={[["What is known?","Everyone needs this.","Three interviewees described the problem."]]}/>)};
