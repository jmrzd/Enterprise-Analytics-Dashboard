/* Integration Studio — public demo UI and authorized one-shot connectors. */
(function () {
"use strict";
const $=id=>document.getElementById(id);
const content=$("dashboardContent"),main=document.querySelector(".main-inner");
if(!content||!main)return;
const state={source:"demo",step:1,preview:null,tables:[],selected:null,map:null,
             busy:false,error:"",success:"",liveEnabled:false,active:false,from:"demo"};
const sourceOptions={
 demo:{name:"Explore uma conexão",detail:"Teste os passos com uma base fictícia, sem senha e sem custos.",icon:"✦"},
 postgres:{name:"PostgreSQL",detail:"Conexão segura a um servidor PostgreSQL aprovado.",icon:"◫"},
 mysql:{name:"MySQL",detail:"Teste um banco MySQL com TLS e acesso somente leitura.",icon:"▤"},
 csv:{name:"Arquivo CSV",detail:"Importe uma planilha de texto e mapeie suas colunas.",icon:"▦"},
 xlsx:{name:"Excel (.xlsx)",detail:"Prévia rápida de uma aba de uma planilha Excel.",icon:"▥"}
};
const escape=x=>String(x??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const money=n=>new Intl.NumberFormat("pt-BR",{style:"currency",currency:"BRL"}).format(n||0);
const progress=()=>'<div class="integration-progress">'+[["01","Origem"],["02","Testar"],["03","Mapear"]].map(([n,name],i)=>
'<span class="integration-step '+(i+1===state.step?"current":i+1<state.step?"done":"")+'"><b>'+(i+1<state.step?"✓":n)+'</b>'+name+'</span>').join("")+'</div>';
const notice=()=>state.error?'<div class="integration-notice error" role="alert">'+escape(state.error)+'</div>':state.success?'<div class="integration-notice ok" role="status">'+escape(state.success)+'</div>':"";
function safeSetState(fields){Object.assign(state,fields);paint();}
function sourceStep(){
return '<h3 class="integration-heading">Escolha como deseja conectar seus dados</h3><p class="integration-sub">Nenhum arquivo ou senha fica salvo. Comece pelo exemplo sem credenciais, ou selecione sua fonte.</p>'+
'<div class="integration-sources">'+Object.entries(sourceOptions).map(([key,v])=>
'<button type="button" class="integration-source '+(state.source===key?"selected":"")+'" data-source="'+key+'">'+
'<span class="integration-source-icon">'+v.icon+'</span><strong>'+escape(v.name)+'</strong><small>'+escape(v.detail)+'</small>'+(state.source===key?'<span class="source-check">✓</span>':"")+'</button>').join("")+'</div>'+
'<div class="integration-actions"><button class="integration-primary" type="button" data-next>Continuar com '+escape(sourceOptions[state.source].name)+' →</button></div>';
}
function dbStep(){
const v=sourceOptions[state.source],enabled=state.liveEnabled;
const port=state.source==="postgres"?"5432":"3306";
return '<h3 class="integration-heading">'+escape(v.name)+' — dados de conexão</h3>'+
'<p class="integration-sub">Informe os dados de um usuário <strong>somente leitura</strong>. O servidor deve ser público, autorizado pelo administrador e possuir certificado TLS válido.</p>'+
(!enabled?'<div class="integration-notice warn"><strong>Teste remoto protegido.</strong> Antes de conectar um banco real, o proprietário do projeto precisa ativar o teste configurando <code>INTEGRATION_ADMIN_TOKEN</code> e <code>INTEGRATION_ALLOWED_HOSTS</code> na Vercel. Assim ninguém usa este site público para testar servidores aleatórios. Você pode experimentar o <strong>modo demonstração</strong> agora.</div>':
'<div class="integration-notice">Teste autorizado disponível. A aplicação usa HTTPS/TLS, testa <code>SELECT 1</code> e lista somente nomes de tabelas e colunas. Não salva senhas, nem copia registros do banco.</div>')+
'<form id="integrationDbForm" autocomplete="off"><div class="integration-field-grid">'+
'<div class="integration-field"><label for="dbHost">Host / endereço do servidor</label><input id="dbHost" name="host" maxlength="253" placeholder="db.suaempresa.com" required autocomplete="off"></div>'+
'<div class="integration-field"><label for="dbPort">Porta</label><input id="dbPort" name="port" type="number" min="1" max="65535" value="'+port+'" required></div>'+
'<div class="integration-field"><label for="dbDatabase">Nome do banco</label><input id="dbDatabase" name="database" maxlength="128" placeholder="empresa_analytics" required autocomplete="off"></div>'+
'<div class="integration-field"><label for="dbUsername">Usuário somente leitura</label><input id="dbUsername" name="username" maxlength="128" placeholder="leitor_dashboard" required autocomplete="off"></div>'+
'<div class="integration-field"><label for="dbPassword">Senha do usuário</label><input id="dbPassword" name="password" type="password" maxlength="1024" required autocomplete="new-password" placeholder="Nunca é armazenada"></div>'+
'<div class="integration-field"><label for="dbAdminToken">Código de autorização do administrador</label><input id="dbAdminToken" name="admin_token" type="password" maxlength="300" required autocomplete="off" placeholder="Autorização do proprietário"></div>'+
'</div><div class="integration-actions"><button type="button" class="integration-outline" data-back>← Voltar</button>'+
'<button class="integration-primary" type="submit" '+(!enabled?'disabled':'')+'>'+(state.busy?"Verificando conexão...":"✓ Testar conexão segura")+'</button>'+
(!enabled?'<button class="integration-outline" type="button" data-demo>Testar com base fictícia</button>':"")+'</div></form>'+
'<p class="integration-footer-note">Este teste não cadastra uma empresa nem atualiza os gráficos do dashboard. Para operar continuamente com dados reais, será necessária autenticação empresarial e um cofre de credenciais por organização.</p>';
}
function fileStep(){
return '<h3 class="integration-heading">Selecione seu arquivo '+(state.source==="csv"?"CSV":"Excel")+'</h3>'+
'<p class="integration-sub">O sistema lê uma pequena amostra e permite mapear os campos. Limite de 1,5 MB. O arquivo não é salvo no servidor.</p>'+
'<div class="integration-notice warn"><strong>Atenção à privacidade:</strong> o arquivo será enviado por HTTPS ao backend da Vercel para leitura temporária. Não use planilhas com informações confidenciais ou dados pessoais sem autorização.</div>'+
'<form id="integrationFileForm"><label class="integration-file-drop"><input id="integrationFileInput" type="file" accept="'+(state.source==="csv"?".csv,text/csv":".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")+'" required>'+
'<span class="integration-file-icon">▥</span><strong id="integrationFileLabel">Clique para selecionar ou arraste o arquivo</strong><span>Formatos '+(state.source==="csv"?"CSV UTF-8":"Excel .xlsx")+' • Até 1,5 MB</span></label>'+
'<div class="integration-actions"><button type="button" class="integration-outline" data-back>← Voltar</button>'+
'<button type="submit" class="integration-primary" '+(state.busy?'disabled':'')+'>'+(state.busy?"Lendo planilha...":"↗ Visualizar colunas")+'</button></div></form>';
}
function demoStep(){
return '<h3 class="integration-heading">Experimente sem configurar nada</h3>'+
'<p class="integration-sub">Esta demonstração usa tabelas e valores fictícios. Você pode testar a seleção de colunas e entender como uma empresa conectaria seus próprios dados.</p>'+
'<div class="integration-notice ok">✦ Nenhuma chave, senha ou banco remoto necessário.</div>'+
'<div class="integration-actions"><button type="button" class="integration-outline" data-back>← Voltar</button>'+
'<button type="button" class="integration-primary" data-demo>✓ Testar conexão demonstrativa</button></div>';
}
function tableView(columns,rows){
if(!columns.length)return '<div class="integration-empty">Nenhuma coluna disponível.</div>';
return '<div class="integration-table"><table><thead><tr>'+columns.map(h=>'<th>'+escape(h)+'</th>').join("")+'</tr></thead><tbody>'+
rows.map(row=>'<tr>'+columns.map((_,i)=>'<td title="'+escape(row[i]??"")+'">'+escape(row[i]??"")+'</td>').join("")+'</tr>').join("")+'</tbody></table></div>';
}
function mapOptions(cols,value){
return '<option value="">Não mapear</option>'+cols.map(c=>'<option value="'+escape(c)+'" '+(c===value?"selected":"")+'>'+escape(c)+'</option>').join("");
}
function bestColumn(cols,words){
return cols.find(c=>words.some(w=>c.toLowerCase().includes(w)))||"";
}
function mappingStep(){
const db=state.preview||{columns:[],rows:[]};
const columns=db.columns||[];
const dateGuess=bestColumn(columns,["data","date","mes","mês"]);
const valueGuess=bestColumn(columns,["valor","receita","fatur","amount","total","price","preço"]);
const categoryGuess=bestColumn(columns,["categoria","category","produto","departamento","cliente","tipo"]);
const tableBlock=state.tables.length?'<div class="integration-mapping"><h3 class="integration-heading">Tabelas encontradas</h3>'+
'<div class="integration-tables">'+state.tables.map((table,i)=>
'<button class="integration-table-selector '+(state.selected===i?"active":"")+'" type="button" data-table="'+i+'"><span><strong>'+escape(table.schema+"."+table.table)+'</strong><small>'+table.columns.length+' colunas descobertas</small></span><span class="integration-status-pill">'+(state.selected===i?"SELECIONADA":"VER COLUNAS")+'</span></button>').join("")+'</div></div>':"";
const summary=state.from==="database"?
'Conexão verificada! Os nomes e tipos de colunas estão disponíveis para mapeamento. Nenhum registro ou senha foi copiado.':
'Amostra importada! Os registros abaixo são apenas uma prévia, não a base completa.';
return '<h3 class="integration-heading">Conexão validada — configure o mapeamento</h3>'+
'<div class="integration-notice ok">✓ '+escape(summary)+'</div>'+
tableBlock+
'<div class="integration-mapping"><strong>Campos analíticos</strong><p class="integration-help">Associe as colunas aos indicadores que pretende analisar. Esse mapeamento fica apenas aberto nesta aba.</p>'+
'<div class="integration-map-grid">'+
'<div class="integration-field"><label for="mapDate">Data / mês</label><select id="mapDate">'+mapOptions(columns,dateGuess)+'</select></div>'+
'<div class="integration-field"><label for="mapValue">Valor / receita</label><select id="mapValue">'+mapOptions(columns,valueGuess)+'</select></div>'+
'<div class="integration-field"><label for="mapCategory">Categoria / produto</label><select id="mapCategory">'+mapOptions(columns,categoryGuess)+'</select></div>'+
'</div><div class="integration-actions"><button class="integration-primary" type="button" data-analyze>✦ Analisar amostra</button><button class="integration-outline" type="button" data-reset>Nova integração</button></div></div>'+
'<div id="integrationAnalysis"></div>'+
'<div class="integration-mapping"><strong>Prévia da estrutura '+(state.preview?.filename?": "+escape(state.preview.filename):"")+'</strong>'+
(state.from==="database"?'<p class="integration-help">Somente metadados de colunas — o sistema não leu os registros da empresa.</p>':
'<p class="integration-help">'+(db.rows?.length||0)+' linhas exibidas (amostra limitada). Não é o total de registros da planilha.</p>')+
tableView(columns,db.rows||[])+'</div>'+
'<div class="integration-footer-note">Para sincronizar dados empresariais automaticamente, será necessário um ambiente autenticado, armazenamento criptografado de conexões e controles de acesso por empresa. Esta versão testa a conexão e prepara o mapeamento, sem salvar credenciais.</div>';
}
function paint(){
const root=$("integrationPage");if(!root)return;
const mainStep=state.step===1?sourceStep():state.step===2?(state.source==="demo"?demoStep():["postgres","mysql"].includes(state.source)?dbStep():fileStep()):mappingStep();
root.innerHTML='<section class="integration-hero"><div><small>◈ DATA CONNECTOR STUDIO / 01</small><h2>Conecte. Valide. Entenda seus dados.</h2>'+
'<p>Um assistente prático para descobrir fontes de dados, testar permissões e mapear campos, sem editar uma linha de código.</p></div><span class="integration-hero-badge">● INTEGRATION LAB</span></section>'+
'<div class="integration-layout"><section class="integration-main-card">'+progress()+notice()+mainStep+'</section>'+
'<aside class="integration-side"><h3>✦ Guia da conexão</h3><div class="integration-timeline">'+
'<div class="integration-time-item"><b>01</b><div><strong>Escolha a fonte</strong><span>PostgreSQL, MySQL, CSV, Excel ou uma base fictícia.</span></div></div>'+
'<div class="integration-time-item"><b>02</b><div><strong>Teste com segurança</strong><span>Validação TLS e metadados; arquivos são lidos só em memória.</span></div></div>'+
'<div class="integration-time-item"><b>03</b><div><strong>Mapeie as colunas</strong><span>Identifique data, valores e categorias para preparar relatórios.</span></div></div></div>'+
'<div class="integration-security"><strong>♢ Privacidade em primeiro lugar</strong><br>Sem salvar senhas ou planilhas. O teste de bancos reais requer uma autorização do administrador e um host previamente aprovado.</div>'+
'<p><strong>O que já funciona?</strong> Prévia de CSV/Excel, exemplo sem senha, verificação real autorizada de PostgreSQL/MySQL e mapeamento de metadados.</p>'+
'<p><strong>Próxima etapa empresarial:</strong> login, isolamento entre empresas e sincronização automática para abastecer o dashboard.</p>'+
'</aside></div>';
}
function demo(){
const sample={
  schema:"demo",table:"vendas_ficticias",columns:[
    {name:"data",type:"date"},{name:"categoria",type:"text"},
    {name:"produto",type:"text"},{name:"receita",type:"numeric"}]};
const rows=[["2026-11-01","Tecnologia","Notebook Pro","3990.00"],["2026-11-02","Acessórios","Teclado mecânico","329.00"],
  ["2026-11-03","Tecnologia","Monitor 27","1150.00"],["2026-11-04","Móveis","Cadeira ergonômica","1250.00"]];
state.preview={columns:sample.columns.map(x=>x.name),rows,filename:"exemplo_ficticio.csv"};
state.tables=[];state.selected=null;state.from="demo";state.step=3;state.error="";
state.success="Conexão simulada: 4 linhas fictícias disponíveis para explorar.";paint();
}
function chooseDbTable(index){
const table=state.tables[index];if(!table)return;
state.selected=index;state.preview={columns:table.columns.map(x=>x.name),rows:[],filename:table.schema+"."+table.table};
state.error="";state.success="Tabela selecionada: "+table.schema+"."+table.table+". Apenas nomes e tipos de colunas são exibidos.";paint();
}
function parseNumber(text){
let v=String(text??"").trim().replace(/[R$\s]/g,"");
if(!v)return null;
if(v.includes(",")&&v.includes("."))v=v.lastIndexOf(",")>v.lastIndexOf(".")?v.replaceAll(".","").replace(",","."):v.replaceAll(",","");
else if(v.includes(","))v=v.replace(",",".");
const n=Number(v);return Number.isFinite(n)?n:null;
}
function analyze(){
const root=$("integrationPage");
const col=state.preview?.columns||[],rows=state.preview?.rows||[];
const date=root.querySelector("#mapDate")?.value||"";
const value=root.querySelector("#mapValue")?.value||"";
const category=root.querySelector("#mapCategory")?.value||"";
state.map={source:state.source,table:state.preview?.filename||"",date,value,category};
const target=$("integrationAnalysis");
if(state.from==="database"){
target.innerHTML='<div class="integration-notice ok"><strong>✓ Mapeamento preparado nesta aba.</strong> Para consultar registros de um banco empresarial, será necessário criar um conector privado com autenticação e permissões por empresa. Este teste já validou o servidor e a estrutura de colunas.</div>';
return;
}
if(!value){
target.innerHTML='<div class="integration-notice warn">Selecione uma coluna de valor para calcular indicadores da amostra.</div>';return;
}
const index=col.indexOf(value);
const numbers=rows.map(r=>parseNumber(r[index])).filter(n=>n!==null);
const sum=numbers.reduce((a,b)=>a+b,0);
const types=category&&col.includes(category)?new Set(rows.map(r=>r[col.indexOf(category)]).filter(Boolean)).size:0;
target.innerHTML='<div class="integration-map-result">'+
'<div><small>Linhas da amostra</small><strong>'+rows.length+'</strong></div>'+
'<div><small>Soma na amostra</small><strong>'+escape(money(sum))+'</strong></div>'+
'<div><small>Categorias na amostra</small><strong>'+types+'</strong></div></div>'+
'<div class="integration-notice ok">✓ Mapeamento analisado nesta aba. '+numbers.length+' de '+rows.length+' linhas exibidas tinham valor numérico. Os totais são <strong>apenas da amostra</strong>, não do arquivo inteiro.</div>';
}
async function testDb(form){
const data=new FormData(form);
const payload={engine:state.source,host:String(data.get("host")||"").trim(),port:Number(data.get("port")),
  database:String(data.get("database")||""),username:String(data.get("username")||""),
  password:String(data.get("password")||""),admin_token:String(data.get("admin_token")||"")};
state.busy=true;state.error="";state.success="";
const button=form.querySelector('[type="submit"]');
if(button){button.disabled=true;button.textContent="Verificando TLS e permissões...";}
try{
const response=await fetch("/api/integrations/test",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload),cache:"no-store",credentials:"same-origin"});
const result=await response.json();
if(!response.ok)throw Error(typeof result.detail==="string"?result.detail:"Não foi possível testar a conexão.");
state.tables=result.tables||[];
state.selected=state.tables.length?0:null;
state.preview=state.tables.length?{columns:state.tables[0].columns.map(c=>c.name),rows:[],filename:state.tables[0].table}:{columns:[],rows:[]};
state.from="database";state.step=3;state.success=result.message;paint();
}catch(e){
state.error=e.message||"Falha ao testar conexão.";
const password=form.querySelector("#dbPassword"),token=form.querySelector("#dbAdminToken");
if(password)password.value="";
if(token)token.value="";
paint();
}finally{
payload.password="";payload.admin_token="";
state.busy=false;
}
}
async function loadFile(form){
const file=$("integrationFileInput")?.files?.[0];
if(!file){state.error="Selecione um arquivo.";paint();return;}
if(file.size>1500000){state.error="O limite para prévia é 1,5 MB.";paint();return;}
state.busy=true;state.error="";const button=form.querySelector('[type="submit"]');
if(button){button.disabled=true;button.textContent="Analisando arquivo...";}
try{
const formData=new FormData();formData.append("file",file,file.name);
const response=await fetch("/api/integrations/file-preview",{method:"POST",body:formData,cache:"no-store"});
const result=await response.json();
if(!response.ok)throw Error(typeof result.detail==="string"?result.detail:"Não foi possível abrir este arquivo.");
state.preview=result;state.tables=[];state.selected=null;state.from="file";state.step=3;state.success=result.message;paint();
}catch(e){state.error=e.message||"Erro de leitura.";paint();}
finally{state.busy=false;}
}
function openIntegrations(){
state.active=true;
const integration=$("integrationPage");
integration.hidden=false;
$("dashboardContent").hidden=true;
const v2=$("v2Module");if(v2)v2.hidden=true;
const comp=$("v3CompareHost");if(comp)comp.hidden=true;
const toolbar=document.querySelector(".toolbar");if(toolbar)toolbar.hidden=true;
document.querySelectorAll("button.nav-item[data-view]").forEach(b=>{
b.classList.remove("active");b.removeAttribute("aria-current");
});
$("integrationsNav").classList.add("active");$("integrationsNav").setAttribute("aria-current","page");
$("pageTitle").innerHTML='Integrações <span class="heading-star">✦</span>';
$("pageSubtitle").textContent="Conecte fontes, teste permissões e prepare os campos para relatórios.";
$("crumbName").textContent="Integrações";
document.title="Integrações | Enterprise Analytics";
$("sidebar").classList.remove("open");$("mobileOverlay").hidden=true;
paint();window.scrollTo({top:0,behavior:"smooth"});
}
function leaveIntegrations(){
if(!state.active)return;
state.active=false;
$("integrationPage").hidden=true;
$("integrationsNav").classList.remove("active");$("integrationsNav").removeAttribute("aria-current");
$("dashboardContent").hidden=false;
const v2=$("v2Module");if(v2)v2.hidden=false;
const comp=$("v3CompareHost");if(comp)comp.hidden=false;
const toolbar=document.querySelector(".toolbar");if(toolbar)toolbar.hidden=false;
}
const nav=document.createElement("button");nav.id="integrationsNav";nav.type="button";nav.className="nav-item integration-link";
nav.innerHTML='<span class="nav-glyph">⌁</span><span>Integrações</span><span class="mini-tag">NOVO</span>';
const ai=$("aiConfigNav"),power=document.querySelector('button[data-view="powerbi"]');
if(power)power.parentNode.insertBefore(nav,power);else if(ai)ai.insertAdjacentElement("afterend",nav);
const section=document.createElement("section");section.id="integrationPage";section.hidden=true;
const footer=main.querySelector("footer");if(footer)main.insertBefore(section,footer);else main.appendChild(section);
nav.addEventListener("click",openIntegrations);
document.querySelectorAll('button.nav-item[data-view]').forEach(b=>b.addEventListener("click",leaveIntegrations));
section.addEventListener("click",e=>{
const b=e.target.closest("button");if(!b)return;
if(b.hasAttribute("data-source")){state.source=b.dataset.source;state.error="";state.success="";paint();}
else if(b.hasAttribute("data-next")){state.step=2;state.error="";state.success="";paint();}
else if(b.hasAttribute("data-back")){state.step=1;state.error="";state.success="";paint();}
else if(b.hasAttribute("data-demo"))demo();
else if(b.hasAttribute("data-table"))chooseDbTable(Number(b.dataset.table));
else if(b.hasAttribute("data-analyze"))analyze();
else if(b.hasAttribute("data-reset")){state.step=1;state.preview=null;state.tables=[];state.selected=null;state.error="";state.success="";paint();}
});
section.addEventListener("submit",e=>{
if(e.target.id==="integrationDbForm"){e.preventDefault();testDb(e.target);}
if(e.target.id==="integrationFileForm"){e.preventDefault();loadFile(e.target);}
});
section.addEventListener("change",e=>{
if(e.target.id==="integrationFileInput"){
const label=$("integrationFileLabel"),f=e.target.files?.[0];
if(label&&f)label.textContent=f.name;
}
});
fetch("/api/integrations/status",{cache:"no-store"}).then(r=>r.json()).then(x=>{
state.liveEnabled=Boolean(x.live_test_enabled);if(state.active)paint();
}).catch(()=>{state.liveEnabled=false;});
})();
