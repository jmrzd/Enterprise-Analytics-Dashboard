/* ENTERPRISE ANALYTICS // NOVA UI 3.0 — mission-control interactions */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const bootstrap=$("dashboard-bootstrap");
if(!bootstrap)return;
let datasets;
try{datasets=JSON.parse(bootstrap.textContent);}catch(e){return;}
const state={modes:Object.create(null),enabled:Object.create(null),compare:false,palette:false,alerts:false};
const color=["#af91ff","#51e8d7","#ffc97f","#ff88c9"];
const escapeHTML=value=>String(value??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const money=value=>new Intl.NumberFormat("pt-BR",{style:"currency",currency:"BRL",maximumFractionDigits:0}).format(Number(value)||0);
const count=value=>new Intl.NumberFormat("pt-BR").format(Number(value)||0);
const percent=value=>(Number(value)||0).toLocaleString("pt-BR",{maximumFractionDigits:1})+"%";
const compact=value=>{
  const n=Number(value)||0;
  return Math.abs(n)>=1000000?(n/1000000).toLocaleString("pt-BR",{maximumFractionDigits:1})+"mi":
         Math.abs(n)>=1000?(n/1000).toLocaleString("pt-BR",{maximumFractionDigits:0})+"mil":count(n);
};
const currentView=()=>document.querySelector("button.nav-item[data-view].active")?.dataset.view||"overview";
const currentPeriod=()=>$("periodSelect")?.value||"90d";
const currentData=()=>datasets[currentPeriod()]||datasets["90d"];
const currentRows=(d)=> {
 const interval=$("granularitySelect")?.value||"auto";
 return (interval==="weekly"||(interval==="auto"&&["30d","90d"].includes(currentPeriod())))?(d.weekly||d.months):d.months;
};
function safeCSSID(s){return String(s).toLowerCase().replace(/[^a-z0-9-]/g,"-").slice(0,80)}
function makeSmooth(points){
 if(points.length===0)return "";
 let d="M "+points[0][0].toFixed(2)+" "+points[0][1].toFixed(2);
 for(let i=1;i<points.length;i++){
  const prev=points[i-1],cur=points[i];
  const halfway=(prev[0]+cur[0])/2;
  d+=" C "+halfway.toFixed(2)+" "+prev[1].toFixed(2)+", "+halfway.toFixed(2)+" "+cur[1].toFixed(2)+", "+cur[0].toFixed(2)+" "+cur[1].toFixed(2);
 }
 return d;
}
function chartDescriptor(panel,d){
 const raw=panel.querySelector(".panel-title, h3")?.textContent?.trim()||"";
 const name=raw.toLocaleLowerCase("pt-BR");
 let series=null,rows=null,format="currency";
 if(/admissões e desligamentos|movimentaç(ã|õ)oes de pessoas/.test(name)){
  series=[{key:"hired",name:"Admissões"},{key:"left",name:"Desligamentos"}];
  rows=d.hrMovements;format="count";
 }else if(/entrada|saída|caixa|despesa|lançamentos financeiros/.test(name)&&
     (/versus|vs\.?| x |fluxo|semana|mês|mensal|e saídas/.test(name))){
  series=[{key:"income",name:"Entradas"},{key:"expense",name:"Saídas"}];
  rows=currentRows(d);
 }else if(/faturamento|receita e lucro|receita x lucro|tendência de receita|performance comercial/.test(name)){
  series=[{key:"revenue",name:"Receita"},{key:"profit",name:"Lucro bruto"}];
  rows=currentRows(d);
 }
 if(!series||!rows?.length)return null;
 return {name:raw,series,rows,format};
}
function plotSVG(descriptor,mode,key){
 const {rows,series,format}=descriptor;
 const W=1000,H=395,L=77,R=28,T=26,B=55,plotW=W-L-R,plotH=H-T-B;
 const visible=series.filter(s=>state.enabled[key]?.[s.key]!==false);
 const metrics=visible.length?visible:series;
 const values=metrics.flatMap(s=>rows.map(row=>Number(row[s.key])||0));
 const peak=Math.max(1,...values)*1.17;
 const floor=Math.min(0,...values);
 const range=Math.max(1,peak-floor);
 const X=i=>L+plotW*(rows.length===1?.5:i/(rows.length-1));
 const Y=n=>T+plotH-(Number(n)-floor)/range*plotH;
 const F=n=>format==="count"?count(n):money(n);
 const id=safeCSSID(key).slice(0,48);
 let svg='<svg class="v3-svg" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="xMidYMid meet" role="img" aria-label="'+escapeHTML(descriptor.name)+'">';
 svg+='<defs>';
 series.forEach((s,i)=>{
  svg+='<linearGradient id="v3fill-'+id+'-'+i+'" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="'+color[i]+'" stop-opacity="'+(mode==="area"?.44:.19)+'"/><stop offset="95%" stop-color="'+color[i]+'" stop-opacity="0"/></linearGradient>';
  svg+='<linearGradient id="v3bar-'+id+'-'+i+'" x1="0" x2="1" y1="0" y2="0"><stop offset="0%" stop-color="'+color[i]+'" stop-opacity=".63"/><stop offset="100%" stop-color="'+color[i]+'"/></linearGradient>';
 });
 svg+='</defs>';
 for(let i=0;i<6;i++){
  const val=floor+range*(5-i)/5;
  const yy=T+plotH*i/5;
  svg+='<line class="v3-svg-grid" x1="'+L+'" x2="'+(W-R)+'" y1="'+yy.toFixed(2)+'" y2="'+yy.toFixed(2)+'"/>';
  svg+='<text x="'+(L-15)+'" y="'+(yy+4).toFixed(2)+'" text-anchor="end" fill="#879bbd" font-size="13">'+escapeHTML(compact(val))+'</text>';
 }
 const step=Math.max(1,Math.ceil(rows.length/8));
 rows.forEach((row,i)=>{
  if(i%step===0||i===rows.length-1)svg+='<text x="'+X(i).toFixed(2)+'" y="'+(H-16)+'" text-anchor="middle" fill="#91a4c5" font-size="13">'+escapeHTML(row.label)+'</text>';
 });
 series.forEach((seriesItem,si)=>{
  if(!visible.some(v=>v.key===seriesItem.key))return;
  const points=rows.map((row,i)=>[X(i),Y(row[seriesItem.key])]);
  if(mode==="bar"){
   const group=plotW/rows.length;
   const barW=Math.max(2,Math.min(24,group/(series.length+1)));
   const start=i=>X(i)-(barW*series.length)/2;
   rows.forEach((row,i)=>{
    const base=Y(0),yy=Y(row[seriesItem.key]);
    svg+='<rect x="'+(start(i)+si*barW).toFixed(2)+'" y="'+Math.min(base,yy).toFixed(2)+'" width="'+(barW-2).toFixed(2)+'" height="'+Math.max(1,Math.abs(base-yy)).toFixed(2)+'" rx="3" fill="url(#v3bar-'+id+'-'+si+')" opacity=".94"><title>'+escapeHTML(row.label+" • "+seriesItem.name+": "+F(row[seriesItem.key]))+'</title></rect>';
   });
  }else{
   const path=makeSmooth(points);
   if(mode==="area"||si===0){
    svg+='<path d="'+path+' L '+X(rows.length-1).toFixed(2)+' '+Y(0).toFixed(2)+' L '+X(0).toFixed(2)+' '+Y(0).toFixed(2)+' Z" fill="url(#v3fill-'+id+'-'+si+')" stroke="none"/>';
   }
   svg+='<path class="v3-svg-pulse" d="'+path+'" fill="none" stroke="'+color[si]+'" stroke-width="'+(mode==="area"?4.5:3.7)+'" stroke-linecap="round" stroke-linejoin="round"/>';
   points.forEach((p,i)=>{svg+='<circle class="v3-graph-dot" cx="'+p[0].toFixed(2)+'" cy="'+p[1].toFixed(2)+'" r="5.3" fill="'+color[si]+'" stroke="#151c30" stroke-width="2"><title>'+escapeHTML(rows[i].label+" • "+seriesItem.name+": "+F(rows[i][seriesItem.key]))+'</title></circle>';});
  }
 });
 // Exact values and vertical crosshair by weekly/monthly interval.
 const hitW=plotW/(Math.max(1,rows.length-1));
 rows.forEach((row,i)=>{
   const left=i===0?L:X(i)-hitW/2;
   const right=i===rows.length-1?W-R:X(i)+hitW/2;
   const description=row.label+"\n"+series.map(s=>s.name+": "+F(row[s.key])).join("\n");
   svg+='<g class="v3-hit-zone"><rect x="'+left.toFixed(2)+'" y="'+T+'" width="'+(right-left).toFixed(2)+'" height="'+plotH+'" fill="transparent" tabindex="0" role="img" data-tip="'+escapeHTML(description)+'" aria-label="'+escapeHTML(description)+'"/><line class="v3-hoverline" x1="'+X(i).toFixed(2)+'" y1="'+T+'" x2="'+X(i).toFixed(2)+'" y2="'+(T+plotH)+'" stroke="#c3b6ff" stroke-opacity=".8" stroke-dasharray="5 5" pointer-events="none"/></g>';
 });
 svg+='</svg>';
 return svg;
}
function renderChart(panel,d){
 const desc=chartDescriptor(panel,d);
 if(!desc)return;
 const key=desc.name;
 const container=panel.querySelector(".chart-area");
 const oldSVG=container?null:panel.querySelector("svg.v2-chart");
 if(!container&&!oldSVG)return;
 const mode=state.modes[key]||"area";
 if(!state.enabled[key])state.enabled[key]=Object.create(null);
 panel.classList.add("v3-graph");
 const head=panel.querySelector(".panel-head")||panel.querySelector("h3");
 if(!panel.querySelector(".v3-chartswitch")){
  const controls=document.createElement("div");
  controls.className="v3-chartswitch";
  controls.setAttribute("role","group");
  controls.setAttribute("aria-label","Tipo de gráfico");
  if(head.tagName==="H3")head.insertAdjacentElement("afterend",controls);
  else head.appendChild(controls);
 }
 const controls=panel.querySelector(".v3-chartswitch");
 controls.innerHTML=[["line","Linha"],["area","Área"],["bar","Barras"]].map(([value,label])=>
  '<button type="button" class="'+(mode===value?"active":"")+'" data-v3-mode="'+value+'" data-v3-key="'+escapeHTML(key)+'" aria-pressed="'+(mode===value)+'">'+label+'</button>'
 ).join("");
 const svg=plotSVG(desc,mode,key);
 let chart=container;
 if(!chart){chart=document.createElement("div");chart.className="chart-area";oldSVG.replaceWith(chart);}
 chart.innerHTML=svg;
 const oldLegend=panel.querySelector(".v3-graph-legend");
 if(oldLegend)oldLegend.remove();
 const legend=document.createElement("div");legend.className="v3-graph-legend";
 legend.innerHTML=desc.series.map((s,i)=>
   '<button type="button" class="'+(state.enabled[key][s.key]===false?"":"active")+'" data-v3-series="'+s.key+'" data-v3-key="'+escapeHTML(key)+'" aria-pressed="'+(state.enabled[key][s.key]!==false)+'"><i style="background:'+color[i]+'"></i>'+escapeHTML(s.name)+'</button>'
 ).join("");
 chart.after(legend);
 const oldSub=panel.querySelector(".v3-graph-sub");
 if(oldSub)oldSub.remove();
 const first=desc.series.find(s=>state.enabled[key][s.key]!==false)||desc.series[0];
 const values=desc.rows.map(r=>Number(r[first.key])||0);
 const maxValue=Math.max(...values),minValue=Math.min(...values);
 const maxIndex=values.indexOf(maxValue);
 const change=values.length>=2&&values[0]?(values[values.length-1]/values[0]-1)*100:null;
 const summary=document.createElement("div");
 summary.className="v3-graph-sub";
 summary.innerHTML='<span>✦ Pico: <strong>'+escapeHTML(desc.format==="count"?count(maxValue):money(maxValue))+'</strong> <small>('+escapeHTML(desc.rows[maxIndex].label)+')</small></span>'+
 '<span>Menor valor: <strong>'+escapeHTML(desc.format==="count"?count(minValue):money(minValue))+'</strong></span>'+
 (change===null?'<span>Comparação indisponível</span>':'<span class="'+(change>=0?"v3-trend-up":"v3-trend-down")+'">'+escapeHTML((change>=0?"+":"")+percent(change))+' entre a primeira e a última faixa</span>');
 legend.after(summary);
}
function decorateCharts(){
 const d=currentData();
 if(!d)return;
 document.querySelectorAll('#dashboardContent .panel, #v2Module .v2-panel').forEach(panel=>renderChart(panel,d));
}

/* Real interval comparison based on the previous N days, not partial months. */
const mainHead=document.querySelector(".page-head");
const compareHost=document.createElement("div");compareHost.id="v3CompareHost";
if(mainHead)mainHead.after(compareHost);
function compareCards(){
 const d=currentData();
 if(!state.compare || !d)return compareHost.innerHTML="";
 const prev=d.comparison;
 if(!prev){
  compareHost.innerHTML='<div class="v3-compare"><div class="v3-compare-head"><strong>Comparação com período anterior</strong><span class="v3-summary-chip">Indisponível para 12 meses</span></div><small>O conjunto demonstrativo contém apenas os últimos 365 dias. Selecione até 180 dias para comparar intervalos completos.</small></div>';
  return;
 }
 const dateToBR=s=>s?.split("-").reverse().join("/")||"—";
 const k=d.kpis;
 const rows=[
   ["Faturamento",k.revenue,prev.revenue,"money"],
   ["Lucro bruto",k.grossProfit,prev.grossProfit,"money"],
   ["Pedidos concluídos",k.orders,prev.orders,"count"],
   ["Saldo de caixa",k.cashBalance,prev.cashBalance,"money"]
 ];
 compareHost.innerHTML='<section class="v3-compare" aria-label="Comparação entre períodos">'+
  '<div class="v3-compare-head"><strong>✧ Comparação com o intervalo anterior</strong><small>'+escapeHTML(dateToBR(prev.from))+' a '+escapeHTML(dateToBR(prev.to))+'</small></div>'+
  '<div class="v3-compare-grid">'+rows.map(([name,current,old,type])=>{
   const variation=old?((current-old)/Math.abs(old)*100):null;
   const delta=current-old;
   return '<div class="v3-compare-item"><small>'+escapeHTML(name)+'</small><strong>'+escapeHTML(type==="count"?count(current):money(current))+'</strong>'+
     '<span class="'+(delta>=0?"up":"down")+'">'+(variation===null?"Sem base anterior":escapeHTML((variation>=0?"+":"")+percent(variation)))+
     ' <span style="opacity:.75">vs. '+escapeHTML(type==="count"?count(old):money(old))+'</span></span></div>';
  }).join("")+'</div><p class="v3-hint" style="margin:12px 0 0">Comparação de janelas inteiras de dias; valores gerados pelo Python. Uma variação positiva de caixa não representa lucro.</p></section>';
}
function makeSpark(points,accent){
 if(!points||points.length<2)return "";
 const vals=points.map(Number),max=Math.max(...vals,1),min=Math.min(...vals,0);
 const den=Math.max(1,max-min);
 const ps=vals.map((v,i)=>[4+(i/(vals.length-1))*111,32-(v-min)/den*28]);
 return '<svg class="v3-kpi-chart" viewBox="0 0 120 40" aria-hidden="true"><path d="'+makeSmooth(ps)+'" fill="none" stroke="'+accent+'" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
}
function decorateMetrics(){
 const d=currentData();
 if(!d)return;
 const rows=d.weekly?.length?d.weekly:d.months;
 document.querySelectorAll('#dashboardContent .metric').forEach((metric,i)=>{
   if(metric.querySelector(".v3-kpi-chart"))return;
   const label=metric.querySelector(".metric-top span")?.textContent?.toLowerCase()||"";
   let values=[],accent=color[i%4];
   if(/faturamento|receita total|receita/.test(label))values=rows.map(r=>r.revenue);
   else if(/lucro/.test(label))values=rows.map(r=>r.profit);
   else if(/saldo|caixa/.test(label))values=rows.map(r=>(r.income||0)-(r.expense||0));
   else if(/entrada/.test(label))values=rows.map(r=>r.income);
   else if(/saída/.test(label))values=rows.map(r=>r.expense);
   metric.insertAdjacentHTML("beforeend",makeSpark(values,accent));
 });
}
function updateCompareButton(){
 const btn=$("v3CompareButton");
 if(!btn)return;
 btn.classList.toggle("active",state.compare);
 btn.setAttribute("aria-pressed",String(state.compare));
 btn.textContent=(state.compare?"✓ ":"◫ ")+"Comparar períodos";
}

/* Keyboard command center: actionable navigation, no disconnected mock buttons. */
const palette=document.createElement("div");
palette.id="v3Palette";palette.className="v3-palette-backdrop";palette.hidden=true;
palette.innerHTML='<section class="v3-palette" role="dialog" aria-modal="true" aria-label="Busca rápida e ações">'+
 '<div class="v3-palette-top"><b>⌕</b><input id="v3CommandInput" type="text" autocomplete="off" placeholder="Buscar módulos, dados e ações..." aria-label="Buscar comandos" maxlength="100"><button type="button" id="v3CommandClose" aria-label="Fechar busca">×</button></div>'+
 '<div class="v3-palette-options" id="v3CommandOptions"></div><div class="v3-keyboard-tip">↑ ↓ para navegar · Enter para abrir · Esc para fechar</div></section>';
document.body.appendChild(palette);
const commandItems=[
 {icon:"▦",title:"Visão geral",description:"Indicadores e insights do dashboard",target:"overview"},
 {icon:"↗",title:"Vendas e faturamento",description:"Módulo comercial",target:"sales"},
 {icon:"▦",title:"Produtos",description:"Ranking e análise de produtos",target:"sales",tab:"products"},
 {icon:"◇",title:"Clientes",description:"Análise de clientes",target:"sales",tab:"clients"},
 {icon:"◫",title:"Financeiro",description:"Fluxo de caixa e gastos",target:"finance"},
 {icon:"◷",title:"Pendências",description:"Contas a vencer no financeiro",target:"finance",tab:"pending"},
 {icon:"◈",title:"Simulador de cenários",description:"Teste preços, custos e contratações",target:"finance",tab:"simulator"},
 {icon:"♧",title:"Recursos Humanos",description:"Quadro de colaboradores",target:"hr"},
 {icon:"▤",title:"Power BI Studio",description:"Datasets e exportação CSV",target:"powerbi"},
 {icon:"⌁",title:"Integrações",description:"Conectar PostgreSQL, MySQL, CSV e Excel",target:"integrations"},
 {icon:"↓",title:"Baixar kit Power BI",description:"Exportação ZIP de seis datasets e DAX",target:"download"},
 {icon:"✦",title:"Assistente IA",description:"Análise e perguntas sobre indicadores",target:"ai"},
 {icon:"⚙",title:"Configurações de IA",description:"Escolher OpenAI ou Gemini",target:"settings"}
];
const normalize=t=>String(t).normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
let filtered=commandItems,keyboardIndex=0;
function renderCommands(){
 const q=normalize($("v3CommandInput")?.value||"");
 filtered=commandItems.filter(o=>normalize(o.title+" "+o.description).includes(q));
 keyboardIndex=0;
 $("v3CommandOptions").innerHTML='<div class="v3-palette-group">NAVEGAÇÃO E AÇÕES</div>'+
 (filtered.length?filtered.map((it,i)=>'<button class="v3-palette-result" data-v3-command="'+i+'" type="button"><span class="v3-palette-icon">'+it.icon+'</span>'+
 '<span><strong>'+escapeHTML(it.title)+'</strong><small>'+escapeHTML(it.description)+'</small></span></button>').join(""):'<div class="v3-palette-empty">Nenhum comando encontrado.</div>');
 const first=$("v3CommandOptions").querySelector(".v3-palette-result");
 if(first)first.style.background="#302e53";
}
function openPalette(){
 palette.hidden=false;
 $("v3CommandInput").value="";
 renderCommands();
 $("v3CommandInput").focus();
 state.palette=true;
}
function closePalette(){
 palette.hidden=true;state.palette=false;
}
function navigate(target,tab){
 if(target==="download"){
   window.location.href="/api/powerbi/kit?period="+encodeURIComponent(currentPeriod());
   return;
 }
 if(target==="integrations"){$("integrationsNav")?.click();return;}
 if(target==="ai"){$("aiNavButton")?.click();return;}
 if(target==="settings"){$("aiConfigNav")?.click();return;}
 const nav=document.querySelector('button.nav-item[data-view="'+target+'"]');
 if(!nav)return;
 nav.click();
 if(tab){
   setTimeout(()=>{
     const tabButton=document.querySelector('#v2Module [data-v2-tab="'+tab+'"]');
     tabButton?.click();
   },60);
 }
}
/* Alerts center from synthetic rules — no invented messages. */
const notifications=document.createElement("div");
notifications.id="v3Notify";notifications.className="v3-notify-popover";notifications.hidden=true;
document.body.appendChild(notifications);
function renderNotifications(){
 const cards=currentData()?.smart?.alerts||[];
 $("v3Notify").innerHTML='<div class="v3-notify-head"><strong>✧ Central de alertas</strong><button type="button" data-v3-close-alerts aria-label="Fechar alertas">×</button></div>'+
 '<div class="v3-notify-list">'+cards.map((a,i)=>'<button type="button" class="v3-notify-item" data-v3-alert-view="'+escapeHTML(a.view)+'">'+
 '<strong>'+escapeHTML((a.level==="attention"?"⚠ ":"✦ ")+a.title)+'</strong><small>'+escapeHTML(a.detail)+'</small></button>').join("")+'</div>'+
 '<div class="v3-keyboard-tip">Regras demonstrativas aplicadas aos dados fictícios.</div>';
 const counter=$("v3AlertsCount");
 if(counter)counter.textContent=String(cards.length);
}
function hideAlerts(){notifications.hidden=true;state.alerts=false;$("v3AlertsButton")?.setAttribute("aria-expanded","false");}
function showAlerts(){
 renderNotifications();notifications.hidden=!notifications.hidden;state.alerts=!notifications.hidden;
}

/* Add functional controls to the existing layout without replacing the app. */
const topRight=document.querySelector(".topbar-right");
if(topRight){
 const search=document.createElement("button");search.id="v3CommandButton";search.type="button";
 search.innerHTML='<span class="v3-search-symbol">⌕</span> Comandos <kbd>Ctrl K</kbd>';
 search.title="Buscar páginas e ferramentas (Ctrl+K)";search.setAttribute("aria-label","Abrir busca de comandos");
 const bell=document.createElement("button");bell.id="v3AlertsButton";bell.type="button";
 bell.innerHTML='♧ <em id="v3AlertsCount">0</em>';
 bell.setAttribute("aria-label","Abrir centro de alertas");bell.setAttribute("aria-expanded","false");
 topRight.prepend(bell);topRight.prepend(search);
 search.addEventListener("click",openPalette);
 bell.addEventListener("click",()=>{showAlerts();bell.setAttribute("aria-expanded",String(state.alerts));});
}
const toolbar=document.querySelector(".toolbar");
if(toolbar){
 const compare=document.createElement("button");compare.id="v3CompareButton";
 compare.type="button";compare.className="v3-compare-btn";
 compare.textContent="◫ Comparar períodos";compare.setAttribute("aria-pressed","false");
 toolbar.appendChild(compare);
 compare.addEventListener("click",()=>{state.compare=!state.compare;updateCompareButton();compareCards();});
}
$("v3CommandClose").addEventListener("click",closePalette);
$("v3CommandInput").addEventListener("input",renderCommands);
$("v3CommandInput").addEventListener("keydown",e=>{
 const buttons=[...document.querySelectorAll("#v3CommandOptions .v3-palette-result")];
 if(e.key==="ArrowDown"||e.key==="ArrowUp"){
  e.preventDefault();
  keyboardIndex=buttons.length?(keyboardIndex+(e.key==="ArrowDown"?1:-1)+buttons.length)%buttons.length:0;
  buttons.forEach((b,i)=>b.style.background=i===keyboardIndex?"#302e53":"transparent");
  buttons[keyboardIndex]?.scrollIntoView({block:"nearest"});
 }else if(e.key==="Enter"){
  e.preventDefault();buttons[keyboardIndex]?.click();
 }
});
palette.addEventListener("click",e=>{if(e.target===palette)closePalette();});
function refreshSite(){
 decorateCharts();
 decorateMetrics();
 compareCards();
 renderNotifications();
 updateCompareButton();
}
document.addEventListener("enterprise:rendered",refreshSite);
document.addEventListener("click",e=>{
 const mode=e.target.closest?.("[data-v3-mode]");
 if(mode){
   const panel=mode.closest(".v3-graph");
   if(panel){state.modes[mode.dataset.v3Key]=mode.dataset.v3Mode;renderChart(panel,currentData());}
   return;
 }
 const series=e.target.closest?.("[data-v3-series]");
 if(series){
   const panel=series.closest(".v3-graph");
   if(!panel)return;
   const key=series.dataset.v3Key;
   const next=!(state.enabled[key]?.[series.dataset.v3Series]!==false);
   state.enabled[key][series.dataset.v3Series]=next;
   if(Object.keys(state.enabled[key]).length>=2 && Object.values(state.enabled[key]).every(v=>v===false)){
     state.enabled[key][series.dataset.v3Series]=true;
   }
   renderChart(panel,currentData());
   return;
 }
 const command=e.target.closest?.("[data-v3-command]");
 if(command){
   const it=filtered[Number(command.dataset.v3Command)];
   closePalette();if(it)navigate(it.target,it.tab);
   return;
 }
 const alert=e.target.closest?.("[data-v3-alert-view]");
 if(alert){
   hideAlerts();navigate(alert.dataset.v3AlertView);
   return;
 }
 if(e.target.closest?.("[data-v3-close-alerts]")){hideAlerts();return;}
 const sideNav=e.target.closest?.('button.nav-item[data-view]');
 if(sideNav){
   hideAlerts();
   // Existing V2 sync() uses a timer. After it has rendered, restore top-of-page.
   setTimeout(()=>{window.scrollTo({top:0,behavior:"smooth"});},85);
   return;
 }
 const subTab=e.target.closest?.("[data-v2-tab]");
 if(subTab){
   setTimeout(()=>{document.getElementById("v2Module")?.scrollIntoView({block:"start",behavior:"smooth"});},60);
   return;
 }
 if(state.alerts&&!e.target.closest?.("#v3Notify")&&!e.target.closest?.("#v3AlertsButton"))hideAlerts();
});
document.addEventListener("keydown",e=>{
 if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){
   e.preventDefault();state.palette?closePalette():openPalette();return;
 }
 if(e.key==="Escape"){closePalette();hideAlerts();$("v3AlertsButton")?.setAttribute("aria-expanded","false");}
});
$("periodSelect")?.addEventListener("change",()=>setTimeout(refreshSite,55));
$("granularitySelect")?.addEventListener("change",()=>setTimeout(refreshSite,55));
$("refreshBtn")?.addEventListener("click",()=>setTimeout(refreshSite,55));
setTimeout(refreshSite,0);
})();
