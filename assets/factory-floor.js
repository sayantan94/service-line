/* A view of the existing prototype state, not a second workflow engine. */
const factoryStages = ['Intake', 'Plan', 'Approval', 'Implement', 'Verify', 'Ready'];
const factoryStations = [[75,85],[245,85],[415,85],[415,235],[245,235],[75,235]];

function factoryPoint(x,y,z=0){return [390+(x-y)*.85,150+(x+y)*.4-z]}
function factoryPoints(points){return points.map(p=>factoryPoint(...p).map(n=>n.toFixed(1)).join(',')).join(' ')}
function factoryPoly(points,fill,stroke='#c1d2df',extra=''){return `<polygon points="${factoryPoints(points)}" fill="${fill}" stroke="${stroke}" stroke-width=".8" stroke-linejoin="round" ${extra}/>`}
function factoryBox(x,y,z,w,d,h,top='#f8fbfd',front='#dbe6ee',side='#e9f0f5'){
  return factoryPoly([[x,y+d,z],[x+w,y+d,z],[x+w,y+d,z+h],[x,y+d,z+h]],front)+
    factoryPoly([[x+w,y,z],[x+w,y+d,z],[x+w,y+d,z+h],[x+w,y,z+h]],side)+
    factoryPoly([[x,y,z+h],[x+w,y,z+h],[x+w,y+d,z+h],[x,y+d,z+h]],top);
}
function factoryPlant(x,y){const [px,py]=factoryPoint(x,y);return `<g transform="translate(${px},${py})"><ellipse cy="1" rx="12" ry="5" fill="#b6c8d5" opacity=".22"/><path d="M-7-13h14L5 0Q0 4-5 0Z" fill="#f9fcff" stroke="#c2d1dc"/><ellipse cy="-13" rx="7" ry="3" fill="#d1dde5"/><path d="M0-13v-27M0-25q-15-3-11-13 12-2 11 13M0-31q14-4 10-13-10 0-10 13M0-20q12 0 13-9-9-5-13 9" stroke="#91a99e" stroke-width="1.5" fill="#a6bbb0"/></g>`}
function factoryAgent(w,x,y){
  const [px,py]=factoryPoint(x,y,22),waiting=['waiting','changes','blocked'].includes(w.status),running=w.status==='running',tint=waiting?'#dec08e':w.executor==='Claude'?'#c6b89d':'#8cbde0';
  return `<g transform="translate(${px},${py})"><ellipse cy="24" rx="14" ry="6" fill="#6c8ca3" opacity=".17"/><path d="M-10 13q0-8 10-8t10 8v7H-10Z" fill="${tint}" stroke="#7995a7" stroke-width=".6"/><path d="M-7 21v5M7 21v5" stroke="#58748b" stroke-width="3" stroke-linecap="round"/><rect x="-14" y="-15" width="28" height="25" rx="9" fill="${tint}" stroke="#7894a8" stroke-width=".7"/><rect x="-10" y="-8" width="20" height="11" rx="5" fill="#f5fbff"/><circle cx="-4" cy="-3" r="1.5" fill="#45667e"/><circle cx="4" cy="-3" r="1.5" fill="#45667e"/><path d="M0-15v-5" stroke="#7894a8"/><circle cy="-22" r="2.7" fill="${waiting?'#c39142':running?'#4f9bce':'#9aaab5'}" class="${running?'agent-busy':''}"/>${waiting?'<circle cx="21" cy="-23" r="8" fill="#fff6e4" stroke="#d6b67e"/><text x="21" y="-20" text-anchor="middle" style="font-size:10px;fill:#a07633">!</text>':''}</g>`;
}
function factoryStation(s,index){
  const [x,y]=factoryStations[index],works=s.items.filter(w=>w.status!=='cancelled'&&lineStage(w)===index),w=works.find(w=>w.id===selected)||works[0],chosen=!!w&&w.id===selected;
  const [lx,ly]=factoryPoint(x,y+53),label=factoryStages[index],screen=index===2?'#bd9c67':'#75a7cb';
  let furniture=factoryBox(x-34,y-22,3,3,3,24)+factoryBox(x+30,y+16,3,3,3,24)+factoryBox(x-35,y-23,27,70,45,5);
  furniture+=factoryBox(x-5,y-11,32,10,6,8,'#c7d9e6')+factoryBox(x-21,y-13,40,42,3,24,'#d5e5ef','#d5e5ef','#bdd0df');
  furniture+=factoryPoly([[x-18,y-9.8,43],[x+18,y-9.8,43],[x+18,y-9.8,61],[x-18,y-9.8,61]],w?'#28485f':'#b6c9d6','#b0c4d3');
  if(w){for(let j=0;j<3;j++)furniture+=factoryPoly([[x-14,y-9.5,47+j*4],[x+(j===1?7:13),y-9.5,47+j*4],[x+(j===1?7:13),y-9.5,48+j*4],[x-14,y-9.5,48+j*4]],j===0?screen:'#7593a8','none')}
  furniture+=factoryBox(x-13,y+5,32,26,11,1,'#d6e2eb');
  furniture+=factoryBox(x+24,y+6,32,5,5,6,'#fff','#d6e1e9');
  furniture+=factoryBox(x-9,y+31,5,18,16,13,'#d9e5ee','#c8d9e5','#d0dfe9');
  if(w)furniture+=factoryAgent(w,x,y+37);
  const aria=w?`${label}: ${w.id}, ${w.title}, ${labels[w.status]}`:`${label}: no work items`;
  return `<g role="button" tabindex="0" data-floor-station="${index}" aria-label="${esc(aria)}" aria-pressed="${chosen}"><title>${esc(aria)}</title>${factoryPoly([[x-50,y-37,1],[x+50,y-37,1],[x+50,y+59,1],[x-50,y+59,1]],'transparent','transparent','class="station-select"')}${furniture}<text x="${lx}" y="${ly+15}" text-anchor="middle" class="floor-stage-label">${String(index+1).padStart(2,'0')} ${label.toUpperCase()}</text>${works.length>1?`<text x="${lx}" y="${ly+29}" text-anchor="middle" style="font-size:9px">${works.length} work items</text>`:''}</g>`;
}
function factoryDrawing(s){
  const others=Object.values(serviceStore).filter(x=>x.id!==s.id),levels=others.slice(0,3),base=levels.length*28;
  let structure='';
  for(let i=levels.length-1;i>=0;i--){const z=-(i+1)*28,t=levels[i];structure+=`<g role="button" tabindex="0" data-floor-service="${esc(t.id)}" aria-label="Focus ${esc(t.name)} floor">${factoryBox(-8,-8,z,516,346,26,'#e9f2f8','#e2ebf2','#d0e0ec')}`;
    for(let x=10;x<490;x+=32)structure+=factoryPoly([[x,338,z+5],[x+24,338,z+5],[x+24,338,z+21],[x,338,z+21]],'#acc4d6','#f8fbfd');
    for(let y=10;y<325;y+=32)structure+=factoryPoly([[508,y,z+5],[508,y+24,z+5],[508,y+24,z+21],[508,y,z+21]],'#b8cedd','#f8fbfd');
    const [tx,ty]=factoryPoint(350,338,z+10);structure+=`<rect x="${tx-75}" y="${ty-12}" width="140" height="19" rx="3" fill="#f5faff" stroke="#c2d5e4"/><text x="${tx-65}" y="${ty+1}" class="floor-front-label">${esc(t.name)}</text></g>`;
  }
  const activeCount=s.items.filter(w=>w.status==='running').length;
  const flow=[[75,85],[245,85],[415,85],[465,160],[415,235],[245,235],[75,235]].map(([x,y])=>factoryPoint(x,y,1).join(',')).join(' ');
  let floor=factoryBox(-8,-8,0,516,346,7,'#f7fafc','#d0e1ee','#e0ebf3');
  for(let x=0;x<=500;x+=50)floor+=factoryPoly([[x,0,7.1],[x+.4,0,7.1],[x+.4,330,7.1],[x,330,7.1]],'#dce7ef','none');
  for(let y=0;y<=330;y+=55)floor+=factoryPoly([[0,y,7.1],[500,y,7.1],[500,y+.4,7.1],[0,y+.4,7.1]],'#dce7ef','none');
  floor+=factoryBox(-8,-8,7,8,346,76,'#ffffff','#eaf2f7','#f3f8fb');
  floor+=factoryBox(0,-8,7,508,8,76,'#ffffff','#eff6fb','#e2edf5');
  for(let x=24;x<470;x+=65){floor+=factoryPoly([[x,.3,19],[x+53,.3,19],[x+53,.3,72],[x,.3,72]],'#dcebf5','#b3cbdc');floor+=factoryPoly([[x+3,.5,22],[x+50,.5,22],[x+50,.5,69],[x+3,.5,69]],'#f5fbff','#dae8f2');}
  floor+=factoryPoly([[.3,50,28],[.3,175,28],[.3,175,65],[.3,50,65]],'#fdfefe','#c4d7e5');
  const [sx,sy]=factoryPoint(.5,112,47);floor+=`<text x="${sx}" y="${sy}" transform="rotate(-25 ${sx} ${sy})" text-anchor="middle" style="font-size:12px;font-weight:550;letter-spacing:1px">SERVICE LINE</text>`;
  floor+=`<polyline points="${flow}" fill="none" stroke="#b7d6ec" stroke-width="2" opacity=".7" class="${activeCount?'flow-dashes':''}"/>`;
  floor+=factoryPlant(22,295)+factoryPlant(470,20);
  floor+=[0,1,2,5,4,3].map(i=>factoryStation(s,i)).join('');
  const [nameX,nameY]=factoryPoint(195,339,-5);floor+=`<g transform="translate(${nameX},${nameY})"><rect x="-65" y="-10" width="130" height="24" rx="4" fill="#f8fcff" stroke="#b8d1e3"/><circle cx="-50" cy="2" r="3" fill="${activeCount?'#75a9cf':'#bca279'}"/><text x="-40" y="6" class="floor-front-label" style="font-weight:600">${esc(s.name.length>17?s.name.slice(0,16)+'…':s.name)}</text></g>`;
  return `<svg class="floor-drawing" viewBox="80 40 770 ${530+Math.max(0,base-56)}" aria-label="${esc(s.name)} factory floor. Six selectable workflow stations." role="group"><defs><filter id="floor-shadow" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="17"/></filter></defs><ellipse cx="454" cy="${477+base}" rx="268" ry="59" fill="#7c9bb2" opacity=".18" filter="url(#floor-shadow)"/>${structure}<g class="floor-selected-level">${floor}</g></svg>`;
}
function factoryFocus(id,workId){selectService(id,workId,'factory')}
function factoryOpenItem(workId,target='plan'){
  if(!items.some(w=>w.id===workId))return;
  selected=workId;page='work';tab=target;const w=current();
  session=w.status==='queued'||!w.approved?'planning':w.phase==='implement'||w.phase==='repair'?'implementation':'verification';
  selectedCheck=w.checkIds[0]||'suite';render();
}
function factoryView(){
  const all=Object.values(serviceStore),s=activeService(),works=all.flatMap(x=>x.items),w=current(),running=works.filter(x=>x.status==='running').length,waiting=works.filter(x=>['waiting','changes','blocked'].includes(x.status)).length,ready=works.filter(x=>x.status==='ready').length;
  const selectedStage=w?factoryStages[lineStage(w)]:null,latest=all.flatMap(service=>service.items.filter(item=>item.events.length).map(item=>({service,item,event:item.events.at(-1)}))).slice(0,3);
  const detail=w?`<div class="floor-work-detail"><div class="floor-detail-top"><span>${esc(w.id)}</span><span>${esc(selectedStage)}</span></div><h3>${esc(w.title)}</h3><p>${esc(w.events.at(-1)?.[1]||w.description)}</p><div class="floor-detail-actions"><button class="btn primary" data-floor-open="${esc(w.id)}" data-floor-tab="${['waiting','changes','queued'].includes(w.status)?'plan':'checks'}">${['waiting','changes'].includes(w.status)?'Review plan':w.status==='queued'?'Open request':'Inspect checks'} ↗</button><button class="btn" data-floor-open="${esc(w.id)}" data-floor-tab="context">Session</button></div><div class="floor-detail-meta"><span>${esc(w.executor)} builds · ${esc(verifierOf(w))} verifies · plan v${w.version} · ${riskLabels[w.risk||'low'].toLowerCase()}</span><span>${w.checkIds.filter(id=>w.results[id]?.status==='passed').length}/${w.checkIds.length} checks passed</span></div></div>`:`<div class="floor-work-detail"><h3>Ready for the first request</h3><p>Add a bug, feature, or maintenance task. Its plan will come back to you for approval.</p><div class="floor-detail-actions"><button class="btn primary" data-action="new-work">Create work item</button></div></div>`;
  return `<div class="floor-page"><header class="floor-header"><div><div class="floor-eyebrow">Local workspace / Overview</div><h1>Factory</h1></div><div class="actions"><div class="floor-view-switch" aria-label="Factory view"><button aria-pressed="true" data-page="factory">Floor</button><button aria-pressed="false" data-page="line">Line</button></div><button class="btn primary" data-action="new-work">${uiIcon('add')} Work item</button></div></header><div class="floor-summary"><span><strong>${String(running).padStart(2,'0')}</strong> working</span><span><strong>${String(waiting).padStart(2,'0')}</strong> need you</span><span><strong>${String(ready).padStart(2,'0')}</strong> ready for review</span><span class="floor-demo">SAMPLE STATE</span></div><div class="floor-layout"><section class="floor-canvas" aria-label="Service floors"><div class="floor-selector"><span class="floor-selector-label">Service floors</span>${all.map((service,i)=>`<button data-floor-service="${esc(service.id)}" aria-pressed="${service.id===s.id}" aria-label="Focus ${esc(service.name)} floor"><span>${String(i+1).padStart(2,'0')}</span><span>${esc(service.name)}</span><i class="floor-indicator ${service.items.some(x=>x.status==='running')?'running':service.items.some(x=>['waiting','changes','blocked'].includes(x.status))?'waiting':''}"></i></button>`).join('')}</div>${factoryDrawing(s)}<div class="floor-legend"><span><i></i>Working</span><span><i class="needs-you"></i>Needs you</span><span><i class="idle"></i>Idle</span></div><span class="floor-caption">Select a station to inspect its work</span></section><aside class="floor-inspector" aria-label="Selected service and work"><div class="floor-inspector-top"><h2>${esc(s.name)}</h2><button class="link" data-page="line" aria-label="Open ${esc(s.name)} factory line">Open line ↗</button></div><div class="floor-service-folder">${esc(s.folder)}</div><div class="floor-section-label"><span>Work on this floor</span><span>${s.items.length}</span></div><div class="floor-work-list">${s.items.map(item=>`<button class="floor-work-row" data-floor-item="${esc(item.id)}" aria-pressed="${item.id===selected}" aria-label="Select ${esc(item.id)}: ${esc(item.title)}"><span class="floor-executor-mark ${item.executor==='Claude'?'claude':''}">${item.executor==='Claude'?'Cl':'Cx'}</span><span><strong>${esc(item.title)}</strong><small>${esc(item.id)} · ${esc(item.executor)}</small>${status(item.status)}</span></button>`).join('')||'<p class="floor-empty">No work items on this floor.</p>'}</div>${detail}</aside></div><footer class="floor-events"><span class="floor-events-label">Latest per item</span><div class="floor-events-list">${latest.map(({service,item,event})=>`<span class="floor-event"><code>${esc(service.name)} / ${esc(item.id)}</code><strong>${esc(event[0])}</strong></span>`).join('')||'<span class="floor-no-activity">No activity recorded.</span>'}</div></footer></div>`;
}

document.addEventListener('click',event=>{
  const target=event.target.closest('[data-floor-service],[data-floor-item],[data-floor-open],[data-floor-station]');if(!target)return;
  if(target.dataset.floorService){factoryFocus(target.dataset.floorService);return}
  if(target.dataset.floorOpen){factoryOpenItem(target.dataset.floorOpen,target.dataset.floorTab);return}
  if(target.dataset.floorItem){selected=target.dataset.floorItem;render();return}
  const stage=Number(target.dataset.floorStation),matches=items.filter(w=>w.status!=='cancelled'&&lineStage(w)===stage);
  if(matches.length){const index=matches.findIndex(w=>w.id===selected);selected=matches[(index+1)%matches.length].id;render();document.querySelector(`[data-floor-station="${stage}"]`)?.focus()}
  else toast(`No work items in ${factoryStages[stage].toLowerCase()}.`);
});
document.addEventListener('keydown',event=>{
  const target=event.target.closest('.floor-drawing [role="button"]');
  if(target&&['Enter',' '].includes(event.key)){event.preventDefault();target.dispatchEvent(new MouseEvent('click',{bubbles:true}))}
});
