import type {Meta,StoryObj} from '@storybook/react-vite';
import {SchemaFlow,processModel,type SchemaModel} from '../src';
export default {title:'Schemas/SchemaFlow',component:SchemaFlow,tags:['autodocs'],parameters:{docs:{description:{component:'OS-C041 · measured native DOM nodes, exact routed SVG endpoints and accessible model equivalent. Separate fixtures demonstrate six actual layouts.'}}}} satisfies Meta<typeof SchemaFlow>;
type Story=StoryObj;
const base=(id:string,purpose:string,nodes:SchemaModel['nodes'],edges:SchemaModel['edges'],groups:SchemaModel['groups_owners']=[]):SchemaModel=>({id,version:'0.2',purpose,audience:'Founder and editorial team · illustrative workflow',reading_direction:'top_to_bottom',nodes,edges,groups_owners:groups,content_source_refs:['DESIGN.md · service narrative; illustrative structural fixtures, not performance evidence'],layout_constraints:['Native readable nodes; measured heights','Labels occupy dedicated gutters','Phone uses vertical routes without shrinking'],visual_token_bindings:['palette.navy','palette.cobalt','palette.marigold-500'],accessible_text_equivalent:edges.map(e=>`${nodes.find(n=>n.id===e.source)?.title} to ${nodes.find(n=>n.id===e.target)?.title}: ${e.branch_label??e.path_label??e.relation_type.replaceAll('_',' ')}.`).join(' ')});
const linearModel={...processModel,id:'OS-DIAGRAM-LINEAR',version:'0.2',edges:processModel.edges.filter(e=>e.id!=='e4'),groups_owners:[]};
const branchModel=base('OS-DIAGRAM-BRANCH','A labeled founder review decision',[
{id:'context',role:'input',title:'Source-backed draft',meaning:'Experience, evidence and buyer context are ready for review.'},
{id:'decision',role:'decision',title:'Founder review',meaning:'Does this preserve meaning, voice and evidence?',owner:'Founder'},
{id:'approved',role:'output',title:'Approved delivery',meaning:'The approved draft is ready to deliver. Publication is a separate action.'},
{id:'revise',role:'process_action',title:'Editorial revision',meaning:'Resolve the requested change before seeking approval again.',owner:'Editor'}],[{id:'b1',source:'context',target:'decision',relation_type:'process_flow'},{id:'b2',source:'decision',target:'approved',relation_type:'control_approval',branch_label:'Approved'},{id:'b3',source:'decision',target:'revise',relation_type:'feedback_revision',branch_label:'Needs revision',path_label:'Clarify meaning'}]);
const layeredModel=base('OS-DIAGRAM-LAYERS','Sources, tools, human review and delivery',[
{id:'source',role:'input',title:'Interview source',meaning:'Preserve the original founder experience.'},
{id:'workspace',role:'tool_system',title:'Editorial workspace',meaning:'Organize source-linked drafts; a tool does not approve them.'},
{id:'reviewer',role:'human_check_owner',title:'Founder approval',meaning:'Check the exact wording and evidence.',owner:'Founder'},
{id:'ready',role:'output',title:'Ready-to-post content',meaning:'Approved content is delivered. No automatic publication is implied.'}],[{id:'l1',source:'source',target:'workspace',relation_type:'data_transfer'},{id:'l2',source:'workspace',target:'reviewer',relation_type:'control_approval'},{id:'l3',source:'reviewer',target:'ready',relation_type:'process_flow'}]);
const swimlaneModel={...layeredModel,id:'OS-DIAGRAM-SWIMLANE',purpose:'Founder and editorial system responsibilities',nodes:layeredModel.nodes.map((n,i)=>({...n,owner:i%2===0?'Founder':'Editorial system'}))};
const comparisonModel=base('OS-DIAGRAM-COMPARISON','Compare wording by the evidence it needs',[
{id:'broad',role:'evidence_note',title:'Broad wording',meaning:'“Every buyer wants this.” No supporting research is supplied.',semantic_status:'gap'},
{id:'scoped',role:'evidence_note',title:'Source-led wording',meaning:'State the source, its scope and the limits of the observation.',semantic_status:'hypothesis'},
{id:'blocked',role:'output',title:'Evidence required',meaning:'Keep the claim out of publication until evidence supports it.'},
{id:'review',role:'human_check_owner',title:'Review exact wording',meaning:'A human checks the source and the wording before approval.',owner:'Founder'}],[{id:'c1',source:'broad',target:'blocked',relation_type:'dependency'},{id:'c2',source:'scoped',target:'review',relation_type:'control_approval'}],[{id:'alternative-a',title:'Alternative A · unsupported scope',meaning:'No customer result is asserted.',member_node_ids:['broad','blocked']},{id:'alternative-b',title:'Alternative B · source-led scope',meaning:'Review is still required.',member_node_ids:['scoped','review']}]);
export const Default:Story={render:()=> <SchemaFlow model={linearModel}/>};
export const LinearFlow:Story={render:()=> <SchemaFlow model={linearModel} layout="linear_flow"/>};
export const LabeledBranch:Story={render:()=> <SchemaFlow model={branchModel} layout="labeled_branch"/>};
export const RevisionLoop:Story={render:()=> <SchemaFlow model={processModel} layout="revision_loop"/>};
export const LayeredArchitecture:Story={render:()=> <SchemaFlow model={layeredModel} layout="layered_architecture"/>};
export const HumanSystemSwimlane:Story={render:()=> <SchemaFlow model={swimlaneModel} layout="human_system_swimlane"/>};
export const Comparison:Story={render:()=> <SchemaFlow model={comparisonModel} layout="comparison"/>};
export const LongLabels:Story={render:()=> <SchemaFlow model={{...processModel,id:'OS-DIAGRAM-LONG',nodes:processModel.nodes.map(n=>({...n,title:n.title+' with a longer descriptive title',meaning:n.meaning+' Preserve the exact founder source, explain the buyer context, and retain qualifications that keep the meaning accurate.'}))}} layout="revision_loop"/>};
export const InvalidModel:Story={render:()=> <SchemaFlow model={{...linearModel,id:'OS-DIAGRAM-INVALID',edges:[{id:'invalid-edge',source:'missing',target:'delivery',relation_type:'dependency'}]}}/>};
