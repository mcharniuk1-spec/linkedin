import * as THREE from 'three';
/** Original sculptural fallback model. Surface folds are artistic, not anatomical data. */
export function createCorticalBrain(){
  const group=new THREE.Group();group.name='Outspoken_original_cortical_brain_artistic';
  const material=new THREE.MeshPhysicalMaterial({color:'#223e80',metalness:.22,roughness:.56,clearcoat:.24,side:THREE.DoubleSide,emissive:'#10275e',emissiveIntensity:.12});
  const geometries:THREE.BufferGeometry[]=[];
  for(const side of [-1,1]){
    const geometry=new THREE.SphereGeometry(1,256,192,-Math.PI/2,Math.PI),position=geometry.getAttribute('position');
    for(let i=0;i<position.count;i++){
      const sx=position.getX(i),sy=position.getY(i),sz=position.getZ(i);
      const az=Math.atan2(sz,sx),elevation=Math.asin(THREE.MathUtils.clamp(sy,-1,1));
      // Curved, irregular sulci occupy a thin band; broad convex gyri stay substantial.
      const warp=1.6*Math.sin(az*3.2+elevation*2.7)+.72*Math.sin(elevation*7.1-az*1.8);
      const foldA=Math.abs(Math.sin(az*7.2+elevation*2.6+warp));
      const foldB=Math.abs(Math.sin(elevation*10.1+az*2.3+Math.sin(az*3.2)*1.6));
      const sulcus=Math.max(Math.exp(-foldA*foldA/.065),Math.exp(-foldB*foldB/.045)*.82);
      const gyrus=1-.085*sulcus+.006*Math.sin(az*13+elevation*15);
      let x=(.035+sx*1.78)*side;
      // Flatten the medial faces to make a readable longitudinal fissure.
      x=side*(.035+Math.abs(sx)*1.78)*gyrus;
      const y=(sy*1.55+.08*Math.cos(sz*2.2))*gyrus;
      const z=sz*(1.83+.13*Math.max(0,sz))*gyrus;
      position.setXYZ(i,x,y,z);
    }
    geometry.computeVertexNormals();geometries.push(geometry);
    const mesh=new THREE.Mesh(geometry,material);mesh.name=side===-1?'left_cortical_hemisphere':'right_cortical_hemisphere';group.add(mesh);
  }
  const cerebellum=new THREE.SphereGeometry(1,96,64),cp=cerebellum.getAttribute('position');
  for(let i=0;i<cp.count;i++){const x=cp.getX(i),y=cp.getY(i),z=cp.getZ(i),r=1-.075*Math.pow(Math.cos(y*27+z*4),8);cp.setXYZ(i,x*1.02*r,y*.52*r-1.24,z*.75*r-.83);}
  cerebellum.computeVertexNormals();geometries.push(cerebellum);const little=new THREE.Mesh(cerebellum,material);little.name='cerebellar_sculpture';group.add(little);
  const stem=new THREE.CylinderGeometry(.23,.13,.9,24,8);stem.rotateX(-.3);stem.translate(0,-1.78,-.48);geometries.push(stem);const stalk=new THREE.Mesh(stem,material);stalk.name='brainstem_sculpture';group.add(stalk);
  return {group,geometries,material};
}
