/* Enterprise Analytics 2.0: data exploration, simulations and Power BI exports. */
(function(){
"use strict";
const $=id=>document.getElementById(id);
const bootstrap=$("dashboard-bootstrap");
if(!bootstrap || !$("dashboardContent"))return;
let datasets;
try{datasets=JSON.parse(bootstrap.textContent);}catch(e){return;}
const basic=$("dashboardContent");
const root=document.createElement("div");root.id="v2Module";
const overlay=document.createElement("div");overlay.id="v2DetailOverlay";overlay.className="v2-detail-backdrop";overlay.hidden=true;
overlay.innerHTML='<section class="v2-detail" role="dialog" aria-modal="true" aria-label="Detalhes do indicador"><button class="v2-detail-close" type="button" aria-label="Fechar detalhes">×</button><div id="v2DetailBody"></div></section>';
document.body.appendChild(overlay);
const tabs={sales:"summary",finance:"cash",hr:"team",powerbi:"datasets"};
const names={
sales:[["summary","Resumo"],["products","Produtos"],["clients","Clientes"],["performance","Performance"]],
finance:[["cash","Fluxo de caixa"],["expenses","Despesas"],["pending","Pendências"],["simulator","Simulador"]],
hr:[["team","Equipe"],["departments","Departamentos"],["movement","Movimentações"],["costs","Custos"]],
powerbi:[["datasets","Datasets"],["model","Modelo de dados"],["dax","Medidas DAX"],["guide","Como usar"]]
};
const C=["#a58bfa","#47dfd2","#f6c577","#fb81c1"];
const currency=n=>new Intl.NumberFormat("pt-BR",{style:"currency",currency:"BRL",maximumFractionDigits:0}).format(Number(n)||0);
const number=n=>new Intl.NumberFormat("pt-BR").format(Number(n)||0);
const pct=n=>(Number(n)||0).toLocaleString("pt-BR",{maximumFractionDigits:1})+"%";
const esc=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const view=()=>document.querySelector("button.nav-item[data-view].active")?.dataset.view||"overview";
const period=()=>$("periodSelect")?.value||"90d";
const data=()=>datasets[period()]||datasets["90d"];
function section(title,desc){return '<div class="v2-heading"><div><h2>'+esc(title)+'</h2>'+(desc?'<p>'+esc(desc)+'</p>':"")+'</div></div>';}
function panel(title,desc,body){return '<section class="v2-panel"><h3>'+esc(title)+'</h3>'+(desc?'<p>'+esc(desc)+'</p>':"")+body+'</section>';}
function mini(label,value,hint){return '<div class="v2-metric"><small>'+esc(label)+'</small><strong>'+esc(value)+'</strong>'+(hint?'<em>'+esc(hint)+'</em>':"")+'</div>';}
function minibar(items,key,kind){
if(!items.length)return "<p>Nenhum dado neste período.</p>";
const max=Math.max(1,...items.map(x=>Number(x[key])||0));
return '<div class="v2-rows">'+items.map((x,i)=>{
const n=Number(x[key])||0;const text=kind==="money"?currency(n):number(n);
return '<button class="v2-data-row" type="button" data-detail="'+esc(x.name)+'"><span class="v2-row-num">'+String(i+1).padStart(2,"0")+'</span><span class="v2-row-main"><strong>'+esc(x.name)+'</strong><span class="v2-progress"><span style="width:'+Math.max(0,n/max*100).toFixed(1)+'%"></span></span></span><span class="v2-row-value">'+text+'</span></button>';
}).join("")+'</div>';
}
function table(heads,rows){return '<div class="v2-table"><table><thead><tr>'+heads.map(x=>'<th>'+esc(x)+'</th>').join("")+'</tr></thead><tbody>'+rows.map(cells=>'<tr>'+cells.map((c,i)=>'<td class="'+(i===0?"table-primary":"")+'">'+esc(c)+'</td>').join("")+'</tr>').join("")+'</tbody></table></div>';}
function tabNav(module){
return '<div class="v2-tabs" role="tablist" aria-label="Painel de '+esc(module)+'">'+names[module].map(([key,name])=>'<button class="v2-tab '+(tabs[module]===key?"active":"")+'" type="button" role="tab" aria-selected="'+(tabs[module]===key)+'" data-v2-tab="'+key+'">'+esc(name)+'</button>').join("")+'</div>';
}
function smartCards(d){
const entries=d.smart?.insights||[];
return '<div class="v2-cards">'+entries.map((s,i)=>'<button class="v2-insight '+(s.kind==="warning"?"warning":"")+'" type="button" data-go="'+esc(s.view)+'"><span class="v2-tag">✦ INSIGHT '+String(i+1).padStart(2,"0")+'</span><span class="v2-value">'+esc(s.value)+'</span><span class="v2-name">'+esc(s.title)+'</span><small>'+esc(s.detail)+'</small></button>').join("")+'</div>';
}
function alerts(d){
return '<div class="v2-alerts">'+(d.smart?.alerts||[]).map(a=>'<button type="button" class="v2-alert '+(a.level==="attention"?"warning":"")+'" data-go="'+esc(a.view)+'"><span class="v2-alert-icon">'+(a.level==="attention"?"!":"i")+'</span><span><strong>'+esc(a.title)+'</strong><small>'+esc(a.detail)+'</small></span></button>').join("")+'</div>';
}
function quickLinks(){
return '<div class="v2-linkgrid">'+[
["sales","↗","Vendas","Produtos, clientes e performance"],
["finance","◫","Financeiro","Fluxo, despesas e simulador"],
["hr","♧","Pessoas","Departamentos e folha"],
["powerbi","▤","Power BI Studio","Baixe os arquivos de análise"]
].map(([key,icon,title,desc])=>'<button class="v2-link" data-go="'+key+'" type="button"><span>'+icon+'</span><strong>'+title+'</strong><small>'+desc+'</small></button>').join("")+'</div>';
}
function intro(tag,title,description){
return '<div class="v2-powerbi-hero"><div><div class="section-kicker">'+esc(tag)+'</div><h3>'+esc(title)+'</h3><p>'+esc(description)+'</p></div><span class="v2-status-chip">● DADOS SINTÉTICOS</span></div>';
}
function overview(d){
return section("Insights executivos","Indicadores automáticos, explicados por regras, sem custo de IA")+smartCards(d)+
section("Alertas inteligentes","Condições demonstrativas baseadas nos seus indicadores")+alerts(d)+
section("Ações rápidas","Explore os módulos e ferramentas do projeto")+quickLinks();
}

function sparkChart(rows,keyA,keyB){
const W=980,H=340,L=75,R=20,T=20,B=48;
if(!rows.length)return "<p>Sem dados para o período.</p>";
const max=Math.max(1,...rows.map(x=>Math.max(x[keyA]||0,x[keyB]||0)))*1.18;
const X=i=>L+(W-L-R)*(rows.length===1?.5:i/(rows.length-1));
const Y=v=>T+(H-T-B)*(1-(Number(v)||0)/max);
let svg='<svg class="v2-chart" viewBox="0 0 '+W+' '+H+'" role="img" aria-label="Gráfico interativo de comparação">';
for(let i=0;i<5;i++){const y=T+(H-T-B)*i/4;svg+='<line x1="'+L+'" y1="'+y+'" x2="'+(W-R)+'" y2="'+y+'" stroke="#2f3a50" stroke-dasharray="5 7"/>';}
for(const [si,key] of [keyA,keyB].entries()){
const pts=rows.map((r,i)=>[X(i),Y(r[key])]);const points=pts.map((p,i)=>(i?"L":"M")+p[0]+" "+p[1]).join(" ");
svg+='<path d="'+points+'" fill="none" stroke="'+C[si]+'" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>';
pts.forEach((p,i)=>{svg+='<circle cx="'+p[0]+'" cy="'+p[1]+'" r="6" fill="'+C[si]+'" stroke="#101827" stroke-width="2"><title>'+esc(rows[i].label+": "+key+" "+currency(rows[i][key]))+'</title></circle>';});
}
const step=Math.max(1,Math.ceil(rows.length/9));
rows.forEach((r,i)=>{if(i%step===0||i===rows.length-1)svg+='<text x="'+X(i)+'" y="'+(H-12)+'" fill="#a5b1ca" font-size="13" text-anchor="middle">'+esc(r.label)+'</text>';});
return svg+'</svg><p class="small-note"><span style="color:'+C[0]+'">●</span> '+esc(keyA)+' &nbsp;&nbsp; <span style="color:'+C[1]+'">●</span> '+esc(keyB)+' • Passe o mouse sobre os pontos.</p>';
}
function salesTab(d){
const k=d.kpis,t=tabs.sales;
if(t==="summary")return "";
if(t==="products")return section("Inteligência de produtos","Clique em um item para abrir o detalhamento")+
'<div class="v2-split">'+panel("Ranking por faturamento","Ranking real dentro dos dados sintéticos",minibar(d.products,"revenue","money"))+
panel("Categorias","Receita agregada por segmento",minibar(d.categories,"value","money"))+'</div>'+
panel("Análise de volumes","Unidades e receita total",table(["Produto","Categoria","Unidades","Receita"],d.products.map(p=>[p.name,p.category||"—",number(p.units),currency(p.revenue)])));
if(t==="clients")return section("Inteligência de clientes","Ranking da amostra demonstrativa (top 6 clientes)")+
'<div class="v2-metrics">'+mini("Receita total",currency(k.revenue),"Pedidos concluídos")+mini("Clientes exibidos",number(d.clients.length),"Amostra: top 6")+mini("Ticket médio",currency(k.avgTicket),"Receita por pedido")+'</div>'+
panel("Principais clientes","Clique para inspecionar a participação na receita",minibar(d.clients,"value","money"))+
panel("Participação","Faturamento por cliente / receita total",table(["Cliente","Receita","% da receita total"],d.clients.map(c=>[c.name,currency(c.value),pct(k.revenue?100*c.value/k.revenue:0)])));
return section("Performance comparativa","Compare séries semanais e mensais sem confundir meses parciais")+
'<div class="v2-metrics">'+mini("Margem bruta",pct(k.margin),"Lucro bruto ÷ receita")+mini("Pedidos",number(k.orders),"Concluídos")+mini("Faturamento",currency(k.revenue),"Período atual")+'</div>'+
panel("Receita e lucro por intervalo","Semanas com maior resolução; meses com visão consolidada",sparkChart(d.weekly||d.months,"revenue","profit"))+
section("Insights de performance","Regras transparentes")+smartCards(d)+alerts(d);
}
function financeTab(d){
const t=tabs.finance,k=d.kpis;
if(t==="cash")return "";
if(t==="expenses")return section("Despesas por categoria","Análise com base nos lançamentos pagos")+
'<div class="v2-metrics">'+mini("Entradas",currency(k.income),"Receitas pagas")+mini("Saídas",currency(k.expenses),"Despesas pagas")+mini("Saldo",currency(k.cashBalance),"Entradas − saídas")+'</div>'+
'<div class="v2-split">'+panel("Centros de custo","Despesas por tipo",minibar(d.expenseCategories,"value","money"))+
panel("Composição dos pagamentos","Distribuição das despesas",table(["Categoria","Gasto"],d.expenseCategories.map(c=>[c.name,currency(c.value)])))+'</div>'+
panel("Entradas e saídas por semana","Fluxos independentes do faturamento",sparkChart(d.weekly||d.months,"income","expense"));
if(t==="pending")return section("Contas pendentes","Agenda sintética; não são contas reais")+
'<div class="v2-metrics">'+mini("Total de contas",number(d.pending.length),"Demonstração")+mini("Valor pendente",currency(d.pending.reduce((s,p)=>s+p.amount,0)),"Compromissos simulados")+mini("Caixa registrado",currency(k.cashBalance),"Lançamentos pagos")+'</div>'+
panel("Próximos vencimentos","Ordenados por data",table(["Descrição","Categoria","Vencimento","Valor"],d.pending.map(p=>[p.name,p.category,p.due.split("-").reverse().join("/"),currency(p.amount)])))+
section("Alertas financeiros","Regras ilustrativas")+alerts(d);
return simulator(d);
}
function hrTab(d){
const t=tabs.hr,k=d.kpis;
if(t==="team")return "";
if(t==="departments")return section("Estrutura organizacional","Informações sintéticas por departamento")+
'<div class="v2-metrics">'+mini("Colaboradores",number(k.headcount),"Ativos")+mini("Departamentos",number(k.departments),"Áreas")+mini("Folha mensal",currency(k.payroll),"Total")+'</div>'+
panel("Departamentos","Clique para detalhar o custo da área",minibar(d.departments,"headcount","count"))+
panel("Quadro e folha","Uma fotografia do quadro atual",table(["Departamento","Colaboradores","Folha mensal","Média por pessoa"],d.departments.map(r=>[r.name,number(r.headcount),currency(r.payroll),currency(r.payroll/r.headcount)])));
if(t==="movement")return section("Pessoas em movimento","Admissões e desligamentos sintéticos do período")+
'<div class="v2-metrics">'+mini("Admissões",number(d.hrMovements.reduce((s,x)=>s+x.hired,0)),"Série de demonstração")+mini("Desligamentos",number(d.hrMovements.reduce((s,x)=>s+x.left,0)),"Série de demonstração")+mini("Headcount atual",number(k.headcount),"Não derivado dos movimentos")+'</div>'+
panel("Movimentações por mês","Indicadores fictícios não conciliados ao quadro atual",
table(["Mês","Admissões","Desligamentos"],d.hrMovements.map(r=>[r.label,number(r.hired),number(r.left)])));
return section("Custos de pessoas","Folha mensal por departamento")+
'<div class="v2-metrics">'+mini("Folha mensal",currency(k.payroll),"Total atual")+mini("Média por colaborador",currency(k.headcount?k.payroll/k.headcount:0),"Média simples")+mini("Equipe",number(k.headcount),"Ativos")+'</div>'+
panel("Folha por departamento","Clique para comparar",minibar(d.departments,"payroll","money"))+
panel("Composição da folha","Custo sintético da equipe",table(["Departamento","Colaboradores","Folha mensal"],d.departments.map(r=>[r.name,number(r.headcount),currency(r.payroll)])));
}
function simulator(d){
const inputs=[
["price","Preço de venda",-25,40,"%"],
["volume","Volume de pedidos",-35,50,"%"],
["cost","Custo dos produtos",-25,40,"%"],
["hires","Novos funcionários",0,15,""],
["expenses","Redução das despesas",0,40,"%"]
];
return '<section class="v2-scenario"><div class="v2-scenario-head"><div><div class="section-kicker">WHAT-IF LAB • SIMULAÇÃO</div><h3>Teste cenários com seus dados</h3><p>Mova os controles para calcular o impacto imediatamente, sem alterar as métricas originais.</p></div><button type="button" class="v2-outline" data-scenario-reset>↺ Restaurar</button></div>'+
'<div class="v2-scenario-layout"><div class="v2-scenario-controls">'+inputs.map(([key,name,min,max,suffix])=>
'<label class="v2-range"><span class="v2-range-label"><span>'+esc(name)+'</span><output data-output="'+key+'">0'+suffix+'</output></span><input type="range" min="'+min+'" max="'+max+'" value="0" step="1" data-input="'+key+'" aria-label="'+esc(name)+'"></label>'
).join("")+'</div><div id="v2ScenarioResults" class="v2-scenario-result"></div></div>'+
'<p class="v2-scenario-disclaimer">Simulação matemática ilustrativa. Vendas, caixa e RH são conjuntos separados; não há previsão de lucro líquido ou reconciliação contábil. Fórmulas: receita × (1+preço%) × (1+volume%); custo dos produtos × (1+custo%) × (1+volume%).</p></section>';
}
function updateScenario(){
const box=document.querySelector(".v2-scenario");if(!box)return;
const k=data().kpis;
const vals={};
box.querySelectorAll("[data-input]").forEach(x=>{
const key=x.dataset.input;const value=Number(x.value);vals[key]=value;
const output=box.querySelector('[data-output="'+key+'"]');
output.textContent=(value>0&&key!=="hires"?"+":"")+number(value)+(key==="hires"?"":"%");
});
const revenue=k.revenue*(1+vals.price/100)*(1+vals.volume/100);
const cogs=(k.revenue-k.grossProfit)*(1+vals.volume/100)*(1+vals.cost/100);
const profit=revenue-cogs;
const margin=revenue?profit/revenue*100:0;
const monthlyIncrement=vals.hires*(k.headcount?k.payroll/k.headcount:0);
const savings=k.expenses*vals.expenses/100;
$("v2ScenarioResults").innerHTML=[
["Receita projetada",currency(revenue),"Diferença: "+currency(revenue-k.revenue)],
["Lucro bruto",currency(profit),"Diferença: "+currency(profit-k.grossProfit)],
["Margem bruta",pct(margin),"Antes: "+pct(k.margin)],
["Economia de despesas",currency(savings),"Sobre lançamentos pagos"],
["Folha mensal",currency(k.payroll+monthlyIncrement),"Acréscimo: "+currency(monthlyIncrement)],
["Colaboradores",number(k.headcount+vals.hires),"+"+number(vals.hires)+" pessoas"]
].map(([name,value,detail])=>mini(name,value,detail)).join("");
}

const PBSETS=[
["vendas","Fato Vendas","Receita, lucro bruto e pedidos","mes_inicio · receita · lucro_bruto · pedidos"],
["financeiro","Fato Financeiro","Entradas, saídas e saldo","mes_inicio · entradas · saidas · saldo"],
["rh","Dim Departamento","Colaboradores e folha mensal","departamento · colaboradores · folha"],
["produtos","Dim Produtos","Unidades e receita por produto","produto · unidades · receita"],
["clientes","Clientes — Top 6","Amostra dos clientes de maior receita","cliente · receita"],
["categorias","Categorias","Composição das vendas","categoria · receita"]
];
const measures=[
"Receita Total = SUM(FatoVendas[receita])",
"Lucro Bruto = SUM(FatoVendas[lucro_bruto])",
"Margem Bruta % = DIVIDE([Lucro Bruto], [Receita Total], 0)",
"Pedidos Concluidos = SUM(FatoVendas[pedidos_concluidos])",
"Ticket Medio = DIVIDE([Receita Total], [Pedidos Concluidos], 0)",
"Entradas = SUM(FatoFinanceiro[entradas])",
"Saidas = SUM(FatoFinanceiro[saidas])",
"Saldo Caixa = [Entradas] - [Saidas]",
"Colaboradores = SUM(DimDepartamento[colaboradores_ativos])",
"Folha Mensal = SUM(DimDepartamento[folha_mensal])"
];
function powerbiTab(d){
const t=tabs.powerbi,p=encodeURIComponent(period());
if(t==="datasets"){
return intro("POWER BI WORKSPACE / EXPORTAÇÃO","Analise seus dados no Power BI","Os seis CSVs agregados são gerados pelo backend Python. O ZIP inclui medidas DAX e instruções de importação.")+
'<p><a class="v2-download primary" href="/api/powerbi/kit?period='+p+'" download="enterprise-analytics-powerbi-kit.zip">↓ Baixar kit completo ZIP</a></p>'+
section("Biblioteca de datasets","Baixe um conjunto ou todos de uma vez")+
'<div class="v2-datasets">'+PBSETS.map(([id,name,detail,cols],i)=>
'<article class="v2-dataset"><span>'+["▥","◫","♧","▦","◇","◈"][i]+'</span><strong>'+esc(name)+'</strong><p>'+esc(detail)+'</p><small>'+esc(cols)+'</small><a href="/api/powerbi/'+id+'?period='+p+'" download="'+id+'.csv">↓ Baixar CSV</a></article>'
).join("")+'</div>'+
section("Prévia de dados","Tabela interativa sincronizada ao período selecionado")+
'<div class="v2-panel v2-preview"><label for="v2PreviewSelect">Dataset: </label><select id="v2PreviewSelect">'+PBSETS.map(([id,name])=>'<option value="'+id+'">'+esc(name)+'</option>').join("")+'</select><div id="v2PreviewBody"></div></div>';
}
if(t==="model"){
return intro("DATA PIPELINE / MODELAGEM","Arquitetura transparente","O repositório possui um banco PostgreSQL local. Nesta vitrine, as tabelas do Power BI vêm de dados sintéticos gerados no Python.")+
section("Fluxo de transformação","Como os dados chegam à análise")+
'<div class="v2-pipeline">'+[
["01","PostgreSQL","Esquema relacional do projeto local"],
["02","Python / Pandas","Consulta e processamento dos dados"],
["03","CSV UTF-8","Tabelas agregadas e exportáveis"],
["04","Power BI Desktop","Importação, medidas e relatórios"]
].map(([n,title,desc])=>'<div class="v2-pipe"><small>'+n+' / PIPELINE</small><strong>'+title+'</strong><span>'+desc+'</span></div>').join("")+'</div>'+
panel("Modelo de dados sugerido","Relacionamentos por mês, sem misturar folhas de RH ou caixa com vendas",
'<div class="v2-metrics">'+mini("DimCalendario","mes_inicio","Uma linha por mês")+mini("FatoVendas","mes_inicio","Receita, pedidos e lucro")+mini("FatoFinanceiro","mes_inicio","Entradas, saídas e saldo")+'</div><p>DimDepartamento é uma fotografia atual da equipe; não relacionar diretamente à FatoVendas. Produtos e clientes são rankings agregados, não registros de pedidos.</p>');
}
if(t==="dax"){
return intro("DATA ANALYST TOOLS","Medidas prontas para estudar","Exemplos DAX para criar cartões, totais e indicadores no Power BI Desktop.")+
section("10 medidas DAX","Renomeie as tabelas conforme as instruções do kit")+
'<div class="v2-panel"><div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:15px"><button class="v2-outline" data-copy-dax type="button">⧉ Copiar medidas</button><a class="v2-download" href="/api/powerbi/dax" download="medidas.dax">↓ Baixar medidas.dax</a></div>'+
'<pre class="v2-code" id="v2DaxCode"><code>'+esc(measures.join("\n\n"))+'</code></pre></div>'+
'<p class="small-note">O arquivo .pbix não está incluído. Estas são medidas e dados de partida, não um relatório pronto.</p>';
}
return intro("POWER BI / GUIA","Do CSV ao primeiro relatório","Faça o processo completo no Power BI Desktop, do download à visualização.")+
section("Passo a passo","Use dados fictícios e valide o modelo")+
'<div class="v2-pipeline">'+[
["01","Baixar kit","Abra Datasets e baixe o ZIP com seis CSVs."],
["02","Importar","No Power BI: Obter Dados → Texto/CSV, UTF-8, ponto e vírgula."],
["03","Tipificar","mes_inicio como Data, moeda como Decimal, contagens como Inteiro."],
["04","Criar medidas","Abra Medidas DAX e copie as fórmulas para as tabelas."]
].map(([n,title,desc])=>'<div class="v2-pipe"><small>PASSO '+n+'</small><strong>'+title+'</strong><span>'+desc+'</span></div>').join("")+'</div>'+
panel("Próximos passos","Monte gráficos de linha, tabelas e cartões a partir dos CSVs.",
'<p>O Power BI Desktop salva seu projeto como .pbix. A conexão direta com o PostgreSQL local pode ser configurada separadamente; a vitrine pública não possui banco de produção.</p><p><a class="v2-download primary" href="/api/powerbi/kit?period='+p+'">↓ Começar com o kit</a></p>');
}
function preview(d){
if(!$("v2PreviewSelect")||!$("v2PreviewBody"))return;
const type=$("v2PreviewSelect").value;let heads=[],rows=[];
if(type==="vendas"){heads=["Mês","Receita","Lucro bruto","Pedidos"];rows=d.months.map(x=>[x.label,currency(x.revenue),currency(x.profit),number(x.orders)]);}
else if(type==="financeiro"){heads=["Mês","Entradas","Saídas","Saldo"];rows=d.months.map(x=>[x.label,currency(x.income),currency(x.expense),currency(x.income-x.expense)]);}
else if(type==="rh"){heads=["Departamento","Colaboradores","Folha"];rows=d.departments.map(x=>[x.name,number(x.headcount),currency(x.payroll)]);}
else if(type==="produtos"){heads=["Produto","Unidades","Receita"];rows=d.products.map(x=>[x.name,number(x.units),currency(x.revenue)]);}
else if(type==="clientes"){heads=["Cliente","Receita"];rows=d.clients.map(x=>[x.name,currency(x.value)]);}
else{heads=["Categoria","Receita"];rows=d.categories.map(x=>[x.name,currency(x.value)]);}
$("v2PreviewBody").innerHTML=table(heads,rows);
}
function go(module){const b=document.querySelector('#nav button[data-view="'+module+'"]')||document.querySelector('button[data-view="'+module+'"]');if(b)b.click();}
function sync(){
const v=view(),d=data();if(!d)return;
root.remove();
if(v==="overview"){
basic.hidden=false;
const hero=basic.querySelector(".hero");
if(hero)hero.after(root);else basic.before(root);
root.innerHTML=overview(d);
enhanceCharts();
}else{
basic.before(root);
root.innerHTML=tabNav(v);
if(v==="powerbi"){root.innerHTML+=powerbiTab(d);basic.hidden=true;preview(d);}
else{
const defaultTab={sales:"summary",finance:"cash",hr:"team"}[v];
const activeTab=tabs[v]||defaultTab;
if(activeTab===defaultTab){basic.hidden=false;enhanceCharts();}
else{
basic.hidden=true;
root.innerHTML+=v==="sales"?salesTab(d):v==="finance"?financeTab(d):hrTab(d);
if(document.querySelector(".v2-scenario"))updateScenario();
}
}
}
document.dispatchEvent(new CustomEvent("enterprise:rendered"));
}
function drill(name){
const d=data();
const item=[...d.products,...d.categories,...d.clients,...d.expenseCategories,...d.departments,...d.statuses].find(x=>x.name===name);
if(!item)return;
let html='<small>EXPLORAR INDICADOR • DADOS SINTÉTICOS</small><h2>'+esc(name)+'</h2>';
if(item.units!==undefined)html+='<p>Foram registradas <strong>'+number(item.units)+'</strong> unidades, totalizando <strong>'+currency(item.revenue)+'</strong> de receita.</p><p>Categoria: <strong>'+esc(item.category||"—")+'</strong>.</p>';
else if(item.headcount!==undefined)html+='<p>Equipe: <strong>'+number(item.headcount)+'</strong> colaboradores. Folha mensal: <strong>'+currency(item.payroll)+'</strong>.</p>';
else html+='<p>Valor: <strong>'+currency(item.value||0)+'</strong> no período selecionado.</p>';
if(d.categories.includes(item)){
const products=d.products.filter(p=>p.category===name);
html+=section("Produtos na categoria","Receita agregada")+minibar(products,"revenue","money");
}
if((item.value!==undefined||item.revenue!==undefined)&&!d.departments.includes(item)){
const amount=item.value??item.revenue;
if(d.categories.includes(item)||d.clients.includes(item)||d.products.includes(item))html+='<p>Participação na receita total: <strong>'+pct(d.kpis.revenue?amount/d.kpis.revenue*100:0)+'</strong>.</p>';
}
html+='<p class="small-note">Esta análise é fictícia e não representa uma operação empresarial real.</p>';
$("v2DetailBody").innerHTML=html;overlay.hidden=false;document.body.classList.add("chart-is-expanded");
overlay.querySelector("button").focus();
}
function closeDrill(){overlay.hidden=true;document.body.classList.remove("chart-is-expanded");}
function enhanceCharts(){
basic.querySelectorAll("article.metric").forEach(box=>{
const title=box.querySelector(".metric-top span")?.textContent||"";
const target=/Faturamento|Lucro|Pedidos|Ticket|Receita/.test(title)?"sales":/Caixa|Entradas|Saídas|Pendências/.test(title)?"finance":/Colaboradores|Funcionários|Folha|Departamentos/.test(title)?"hr":null;
if(target){box.classList.add("v2-kpi-click");box.setAttribute("role","button");box.setAttribute("tabindex","0");box.dataset.goto=target;box.setAttribute("aria-label",title+": explorar "+target);}
});
basic.querySelectorAll(".legend span").forEach((element,index)=>{
if(element.dataset.v2Toggle)return;
element.dataset.v2Toggle="1";element.setAttribute("role","button");element.setAttribute("tabindex","0");
element.title="Clique para mostrar/ocultar esta série";
});
basic.querySelectorAll(".donut svg circle[stroke],.hbar-item").forEach(el=>{
if(el.dataset.v2Drill)return;
let name="";
if(el.classList.contains("hbar-item"))name=el.querySelector(".hbar-top strong")?.textContent||"";
else name=el.querySelector("title")?.textContent?.split(":")[0]||"";
if(name&&[...data().products,...data().categories,...data().clients,...data().expenseCategories,...data().departments].some(x=>x.name===name)){
el.dataset.v2Drill=name;el.setAttribute("role","button");el.setAttribute("tabindex","0");el.style.cursor="pointer";
}
});
}

function toggleLegend(element){
const panel=element.closest(".panel");const svg=panel?.querySelector(".chart-area svg");
if(!svg)return;
const siblings=[...element.parentElement.querySelectorAll(".legend span")];
const idx=siblings.indexOf(element);
if(idx<0)return;
const hidden=element.classList.toggle("v2-muted");
const paths=[...svg.querySelectorAll("path[stroke]")].filter(p=>p.getAttribute("stroke")!=="none");
if(paths[idx])paths[idx].classList.toggle("v2-chart-hidden",hidden);
const markers=[...svg.querySelectorAll(".chart-point")];
const count=siblings.length?Math.floor(markers.length/siblings.length):0;
markers.slice(idx*count,idx*count+count).forEach(p=>p.classList.toggle("v2-chart-hidden",hidden));
}
function clickHandler(e){
const b=e.target.closest&&e.target.closest("[data-v2-tab]");
if(b){
const v=view();if(!tabs[v])return;
tabs[v]=b.dataset.v2Tab;sync();
root.scrollIntoView({behavior:"smooth",block:"start"});
return;
}
const goBtn=e.target.closest&&e.target.closest("[data-go]");
if(goBtn){go(goBtn.dataset.go);return;}
const detail=e.target.closest&&e.target.closest("[data-detail], [data-v2-drill]");
if(detail){drill(detail.dataset.detail||detail.dataset.v2Drill);return;}
const kpi=e.target.closest&&e.target.closest("[data-goto]");
if(kpi){go(kpi.dataset.goto);return;}
const legend=e.target.closest&&e.target.closest(".legend span[data-v2-toggle]");
if(legend){toggleLegend(legend);return;}
const reset=e.target.closest&&e.target.closest("[data-scenario-reset]");
if(reset){root.querySelectorAll("[data-input]").forEach(x=>x.value="0");updateScenario();return;}
const copy=e.target.closest&&e.target.closest("[data-copy-dax]");
if(copy){
if(navigator.clipboard&&navigator.clipboard.writeText){
navigator.clipboard.writeText(measures.join("\n\n")).then(()=>{copy.textContent="✓ Copiado";setTimeout(()=>{copy.textContent="⧉ Copiar medidas";},2200);}).catch(()=>{copy.textContent="Use o download .dax";});
}else copy.textContent="Use o download .dax";
return;
}
}
document.addEventListener("click",clickHandler);
document.addEventListener("keydown",e=>{
if(e.key==="Escape")closeDrill();
if(e.key!=="Enter"&&e.key!==" ")return;
const target=e.target;
if(target.matches('[data-goto], [data-v2-drill], .legend span[data-v2-toggle]')){
e.preventDefault();target.click();
}
});
root.addEventListener("input",e=>{if(e.target.matches("[data-input]"))updateScenario();});
root.addEventListener("change",e=>{if(e.target.matches("#v2PreviewSelect"))preview(data());});
overlay.querySelector(".v2-detail-close").addEventListener("click",closeDrill);
overlay.addEventListener("click",e=>{if(e.target===overlay)closeDrill();});
document.querySelectorAll("button[data-view]").forEach(b=>b.addEventListener("click",()=>setTimeout(sync,0)));
$("periodSelect")?.addEventListener("change",()=>setTimeout(sync,0));
$("granularitySelect")?.addEventListener("change",()=>setTimeout(sync,0));
$("refreshBtn")?.addEventListener("click",()=>setTimeout(sync,0));
sync();
})();
