import type { Meta, StoryObj } from '@storybook/react-vite';
import { SpatialScene,FounderChapterStudy } from '../src';
export default {title:'Scenes/Spatial studies',component:SpatialScene} satisfies Meta<typeof SpatialScene>;
export const Founder:StoryObj={render:()=> <SpatialScene/>};
export const Constellation:StoryObj={render:()=> <SpatialScene kind="constellation"/>};
export const StaticFallback:StoryObj={render:()=> <SpatialScene kind="constellation" staticOnly/>};
export const ChapterStudy:StoryObj={render:()=> <FounderChapterStudy/>};
