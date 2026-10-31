import {ExperienceStory} from './ExperienceStory';
import {WhyOutspoken} from './WhyOutspoken';
import type {Meta,StoryObj} from '@storybook/react-vite';
import {AtmosphereHero,ServiceStack,PricePlans,CustomerOpinion,ProcessRail,ClosingPanel,PostCard,RevealHeading,SoundWaves} from './App';
import './website.css';
const meta={title:'V3/Website blocks',parameters:{layout:'fullscreen'},tags:['autodocs']} satisfies Meta;export default meta;type Story=StoryObj<typeof meta>;
export const Hero:Story={render:()=> <AtmosphereHero/>};
export const Experience:Story={render:()=> <ExperienceStory/>};
export const ExperienceRail:Story={render:()=> <ExperienceStory forceRail/>};
export const WhyOutspokenBlock:Story={render:()=> <WhyOutspoken/>};
export const Services:Story={render:()=> <ServiceStack full/>};
export const Pricing:Story={render:()=> <PricePlans/>};
export const Emails:Story={render:()=> <CustomerOpinion/>};
export const Process:Story={render:()=> <ProcessRail/>};
export const Closing:Story={render:()=> <ClosingPanel/>};
export const Heading:Story={render:()=> <div className="section"><RevealHeading>A clear <span className="highlight">point of view.</span></RevealHeading></div>};
export const Resonance:Story={render:()=> <div style={{position:'relative',height:700,overflow:'hidden',background:'#F7F8F6'}}><SoundWaves/></div>};

