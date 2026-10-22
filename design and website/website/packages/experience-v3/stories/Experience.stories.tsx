import type { Meta, StoryObj } from '@storybook/react-vite';
import { ThreeTiltButton, PerspectiveVideo } from '../index';
const meta = {title:'Experience V3/Perspective media',component:PerspectiveVideo,parameters:{layout:'padded'},args:{poster:'/assets/revisions/v5/people/founder-blue.webp',src:'/video/revisions/v5/Outspoken-v5-style-proof-landscape.mp4',title:'A perspective worth sharing',description:'Demonstration film — an original Outspoken style study.',caption:'Open the plate to focus the film. Escape returns to this position.'}} satisfies Meta<typeof PerspectiveVideo>;
export default meta;
type Story = StoryObj<typeof meta>;
export const LeftPlate: Story = {};
export const RightPlate: Story = {args:{tilt:'right'}};
export const Buttons: Story = {render:()=> <div style={{display:'flex',flexWrap:'wrap',gap:28,padding:24}}><ThreeTiltButton>Book an intro call</ThreeTiltButton><ThreeTiltButton tone="citron">Explore the approach</ThreeTiltButton><ThreeTiltButton variant="secondary" tone="silver">View services</ThreeTiltButton><ThreeTiltButton loading>Preparing</ThreeTiltButton><ThreeTiltButton disabled>Unavailable</ThreeTiltButton></div>};
