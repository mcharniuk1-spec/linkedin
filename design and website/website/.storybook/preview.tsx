import type { Preview } from '@storybook/react-vite';
import { MotionConfig } from 'motion/react';
import '../packages/ui/src/styles.css';
const preview: Preview = {
  decorators: [(Story) => <MotionConfig reducedMotion="user"><div className="os-story"><Story /></div></MotionConfig>],
  parameters: {layout:'padded', a11y:{test:'error'}, controls:{expanded:true}, viewport:{options:{phone:{name:'Phone 360',styles:{width:'360px',height:'800px'}},tablet:{name:'Tablet 768',styles:{width:'768px',height:'1024px'}},desktop:{name:'Desktop 1440',styles:{width:'1440px',height:'1000px'}}}}, options:{storySort:{order:['Foundations','Actions','Forms','Navigation','Content','Banners','Chat','Schemas','Editorial','Video','Scenes','Motion','Pilots']}}},
};
export default preview;
