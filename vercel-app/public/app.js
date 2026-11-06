/* Enterprise Analytics — accessible, dependency-free dashboard UI. */
(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const COLORS = ["#a38bff", "#40e0d0", "#f7c26d", "#ff7bb5", "#648fff", "#80cfa8"];
  const VIEWS = {
    overview: ["Visão geral", "Visão inteligente da operação, finanças e pessoas."],
    sales: ["Vendas & faturamento", "Performance comercial, clientes e rentabilidade."],
    finance: ["Gestão financeira", "Entradas, saídas e visibilidade do fluxo de caixa."],
    hr: ["Recursos Humanos", "Indicadores estratégicos de pessoas e departamentos."],
    powerbi: ["Integração Power BI", "Do PostgreSQL ao relatório executivo: a arquitetura do projeto."]
  };
  const state = { view: "overview", period: "90d", data: null, request: 0 };
  const currency = (v) => new Intl.NumberFormat("pt-BR", {style:"currency",currency:"BRL",maximumFractionDigits:0}).format(Number(v)||0);
  const moneyFull = (v) => new Intl.NumberFormat("pt-BR", {style:"currency",currency:"BRL"}).format(Number(v)||0);
  const integer = (v) => new Intl.NumberFormat("pt-BR").format(Number(v)||0);
  const pct = (v) => (Number(v)||0).toLocaleString("pt-BR",{maximumFractionDigits:1}) + "%";
  const short = (v) => {const n=Number(v)||0;return Math.abs(n)>=1e6 ? (n/1e6).toLocaleString("pt-BR",{maximumFractionDigits:1})+" mi" : Math.abs(n)>=1000 ? (n/1000).toLocaleString("pt-BR",{maximumFractionDigits:0})+" mil" : integer(n);};
  const esc = (value) => String(value==null?"":value).replace(/[&<>"']/g,(c)=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const formatDate = (s) => {if(!s)return "—";const p=s.split("-");return p.length===3?p[2]+"/"+p[1]+"/"+p[0]:s;};
  const el = (tag, cls, content) => "<"+tag+(cls?' class="'+cls+'"':"")+">"+content+"</"+tag+">";
  const title = (name,subtitle,extra) => '<div class="panel-head"><div><h3 class="panel-title">'+esc(name)+'</h3><p class="panel-sub">'+esc(subtitle||"")+'</p></div>'+(extra?'<span class="panel-pill">'+esc(extra)+'</span>':"")+"</div>";
  const panel = (name,subtitle,body,extra) => '<section class="panel">'+title(name,subtitle,extra)+body+"</section>";
  const section = (name,sub) => '<div class="section-head"><h2>'+esc(name)+'</h2>'+(sub?'<small>'+esc(sub)+'</small>':"")+"</div>";
  const note = '<div class="callout"><strong>Sobre estes dados:</strong> todos os números são fictícios e gerados em Python. Vendas, caixa e folha salarial são conjuntos independentes; saldo de caixa não representa lucro líquido.</div>';

  function metric(label,value,foot,icon,color) {
    return '<article class="metric"><div class="metric-top"><span>'+esc(label)+'</span><span class="metric-icon '+(color||"")+'">'+esc(icon||"◈")+'</span></div><div class="big-number">'+esc(value)+'</div><div class="metric-foot">'+esc(foot||"Indicador do período")+'</div></article>';
  }
  function metrics(cards) { return '<div class="metric-grid">'+cards.map(c=>metric.apply(null,c)).join("")+"</div>"; }
  function hero(tag,headline,description,badge) {
    return '<section class="hero"><div class="hero-content"><div class="hero-tag">✦ '+esc(tag)+'</div><h2>'+esc(headline)+'</h2><p>'+esc(description)+'</p></div><div class="hero-badge"><span>●</span>'+esc(badge||"LIVE ANALYTICS")+"</div></section>";
  }
  function legend(series) {return '<div class="legend">'+series.map((s,i)=>'<span><i style="background:'+esc(s.color||COLORS[i])+'"></i>'+esc(s.label)+'</span>').join("")+'</div>';}

  function lineChart(rows, series, alt) {
    if (!rows.length) return '<div class="empty-state">Nenhum dado disponível neste período.</div>';
    const W=800,H=278,L=67,R=15,T=18,B=43;
    const pw=W-L-R, ph=H-T-B;
    const max=Math.max(1,...rows.flatMap(r=>series.map(s=>Number(r[s.key])||0)))*1.13;
    const x=(i)=>L+pw*(rows.length===1?.5:i/(rows.length-1));
    const y=(v)=>T+ph-(Number(v)||0)/max*ph;
    let svg='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(alt||"Gráfico de linhas")+'">';
    svg+='<defs><linearGradient id="lineArea" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#9e80ff" stop-opacity=".27"/><stop offset="100%" stop-color="#9e80ff" stop-opacity="0"/></linearGradient></defs>';
    for(let i=0;i<5;i++){
      const value=max*(4-i)/4, yy=T+i*ph/4;
      svg+='<line x1="'+L+'" x2="'+(W-R)+'" y1="'+yy+'" y2="'+yy+'" stroke="#2a3448" stroke-dasharray="4 5"/>';
      svg+='<text x="'+(L-12)+'" y="'+(yy+4)+'" text-anchor="end" font-size="11" fill="#8290ac">'+esc(short(value))+'</text>';
    }
    const step=Math.max(1,Math.ceil(rows.length/7));
    rows.forEach((r,i)=>{if(i%step===0||i===rows.length-1)svg+='<text x="'+x(i)+'" y="'+(H-12)+'" text-anchor="middle" font-size="11" fill="#8996b0">'+esc(r.label)+'</text>';});
    series.forEach((s,idx)=>{
      const points=rows.map((r,i)=>[x(i),y(r[s.key])]);
      const d=points.map((p,i)=>(i?"L":"M")+p[0].toFixed(1)+" "+p[1].toFixed(1)).join(" ");
      if(idx===0)svg+='<path d="'+d+' L '+x(rows.length-1)+' '+(H-B)+' L '+x(0)+' '+(H-B)+' Z" fill="url(#lineArea)"/>';
      svg+='<path d="'+d+'" fill="none" stroke="'+esc(s.color||COLORS[idx])+'" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>';
      points.forEach((p,i)=>{
        svg+='<circle cx="'+p[0]+'" cy="'+p[1]+'" r="4.3" fill="'+esc(s.color||COLORS[idx])+'" stroke="#171d2d" stroke-width="2"><title>'+esc(rows[i].label+": "+s.label+" "+moneyFull(rows[i][s.key]))+'</title></circle>';
      });
    });
    return '<div class="chart-area">'+svg+'</svg></div>'+legend(series);
  }
  function donut(items,caption,unit) {
    const total=items.reduce((a,b)=>a+(Number(b.value)||0),0);
    if(!total)return '<div class="empty-state">Sem dados.</div>';
    const r=71,c=2*Math.PI*r;let used=0;
    let circles='<circle cx="100" cy="100" r="'+r+'" fill="none" stroke="#283046" stroke-width="19"/>';
    items.forEach((item,i)=>{
      const portion=(Number(item.value)||0)/total;
      circles+='<circle cx="100" cy="100" r="'+r+'" fill="none" stroke="'+COLORS[i%COLORS.length]+'" stroke-width="19" stroke-dasharray="'+(portion*c)+' '+c+'" stroke-dashoffset="'+(-used*c)+'"><title>'+esc(item.name+": "+(unit==="currency"?currency(item.value):integer(item.value)))+'</title></circle>';
      used+=portion;
    });
    const legendRows=items.map((item,i)=>'<div class="donut-row"><i style="background:'+COLORS[i%COLORS.length]+'"></i><span>'+esc(item.name)+'</span><strong>'+pct(100*item.value/total)+'</strong></div>').join("");
    return '<div class="donut-layout"><div class="donut"><svg viewBox="0 0 200 200" role="img" aria-label="'+esc(caption)+'">'+circles+'</svg><div class="donut-center"><strong>'+esc(unit==="currency"?short(total):integer(total))+'</strong><span>'+esc(caption)+'</span></div></div><div class="donut-legend">'+legendRows+'</div></div>';
  }
  function barList(items,valueKey,unit,variant) {
    if(!items.length)return '<div class="empty-state">Sem dados.</div>';
    const max=Math.max(1,...items.map(r=>Number(r[valueKey])||0));
    return '<div class="hbar-list">'+items.map((r,i)=>{
      const value=Number(r[valueKey])||0, width=Math.max(1,value/max*100);
      return '<div class="hbar-item"><div class="hbar-top"><strong>'+esc(r.name)+'</strong><span>'+esc(unit==="currency"?currency(value):integer(value))+'</span></div><div class="hbar-track"><div class="hbar-fill '+(variant|| (i%3===1?"cyan":i%3===2?"amber":""))+'" style="width:'+width.toFixed(2)+'%"></div></div></div>';
    }).join("")+'</div>';
  }
  function table(headers,rows) {
    return '<div class="table-wrap"><table><thead><tr>'+headers.map(h=>'<th>'+esc(h)+'</th>').join("")+'</tr></thead><tbody>'+rows.join("")+'</tbody></table></div>';
  }
  function recentTable(rows) {
    return table(["CLIENTE","DATA","VALOR","STATUS"],rows.map(r=>
      '<tr><td><div class="table-client"><span class="table-avatar">'+esc(r.client.slice(0,1))+'</span><div><div class="table-primary">'+esc(r.client)+'</div><div class="table-secondary">'+esc(r.city)+'</div></div></div></td><td>'+esc(formatDate(r.date))+'</td><td class="table-primary">'+esc(currency(r.amount))+'</td><td><span class="status-chip">'+esc(r.status)+'</span></td></tr>'
    ));
  }
  function insightCards(rows) {
    return '<div class="insight-grid">'+rows.map((r,i)=>
      '<div class="insight"><div class="insight-icon">'+(["✦","↗","◈"][i%3])+'</div><h3>'+esc(r.title)+'</h3><strong>'+esc(r.format==="currency"?currency(r.value):r.format==="percent"?pct(r.value):r.value)+'</strong><p>'+esc(r.description)+'</p></div>'
    ).join("")+'</div>';
  }
  function overview(d) {
    const k=d.kpis;
    return hero("CENTRO DE INTELIGÊNCIA","Seus dados. Uma nova perspectiva.","Explore os indicadores mais importantes em uma experiência unificada e interativa.","VISÃO 360°")+
      section("Indicadores estratégicos","Dados do período selecionado")+
      metrics([
        ["Faturamento",currency(k.revenue),"Pedidos concluídos","↗",""],
        ["Lucro bruto",currency(k.grossProfit),"Margem "+pct(k.margin),"◈","cyan"],
        ["Saldo de caixa",currency(k.cashBalance),"Lançamentos pagos","◫","amber"],
        ["Colaboradores",integer(k.headcount),"Quadro atual da empresa","♧","pink"]
      ])+
      section("Análise de performance","Tendências e distribuição")+
      '<div class="grid-2">'+
        panel("Evolução de faturamento","Receita e lucro bruto por mês",lineChart(d.months,[{key:"revenue",label:"Receita",color:COLORS[0]},{key:"profit",label:"Lucro bruto",color:COLORS[1]}],"Receita e lucro bruto"),"PERÍODO")+
        panel("Mix de vendas","Participação por categoria",donut(d.categories,"Receita","currency"),"CATEGORIAS")+
      '</div>'+
      section("Operação em movimento","Últimas transações e produtos")+
      '<div class="grid-2">'+
        panel("Últimas vendas","Pedidos concluídos mais recentes",recentTable(d.recent),"ATUALIZADO")+
        panel("Produtos em destaque","Top 5 por faturamento",barList(d.products.slice(0,5),"revenue","currency"),"TOP 05")+
      '</div>'+
      section("Inteligência de negócio","Insights calculados a partir dos dados")+
      insightCards(d.insights)+note;
  }
  function sales(d) {
    const k=d.kpis;
    return hero("COMERCIAL / PERFORMANCE","Crescimento com clareza.","Acompanhe receita, margem, pedidos e oportunidades de vendas.","SALES ANALYTICS")+
      section("KPIs comerciais","Pedidos concluídos no período")+
      metrics([
        ["Receita total",currency(k.revenue),"Faturamento bruto","↗",""],
        ["Lucro bruto",currency(k.grossProfit),"Receita − custo dos itens","◈","cyan"],
        ["Pedidos",integer(k.orders),"Concluídos no período","▦","amber"],
        ["Ticket médio",currency(k.avgTicket),"Receita por pedido","◇","pink"]
      ])+
      section("Performance comercial","Evolução e composição")+
      '<div class="grid-2">'+
        panel("Receita x lucro bruto","Tendência mensal",lineChart(d.months,[{key:"revenue",label:"Receita",color:COLORS[0]},{key:"profit",label:"Lucro bruto",color:COLORS[1]}],"Receita e lucro bruto"),"MENSAL")+
        panel("Status dos pedidos","Pedidos concluídos, pendentes e cancelados",donut(d.statuses,"Pedidos","count"),"STATUS")+
      '</div>'+
      section("Produtos e clientes","Desempenho por segmento")+
      '<div class="grid-2 grid-even">'+
        panel("Produtos mais rentáveis","Ranking por faturamento",barList(d.products.slice(0,6),"revenue","currency"),"TOP 06")+
        panel("Principais clientes","Receita acumulada por cliente",barList(d.clients,"value","currency","cyan"),"TOP 06")+
      '</div>'+
      panel("Vendas por categoria","Participação no faturamento",donut(d.categories,"Receita","currency"))+note;
  }
  function finance(d) {
    const k=d.kpis;
    return hero("FINANÇAS / CONTROLE","Decisões com confiança.","Uma leitura clara das movimentações financeiras e compromissos futuros.","FINANCE HUB")+
      section("Resumo financeiro","Lançamentos efetivamente pagos")+
      metrics([
        ["Entradas",currency(k.income),"Receitas pagas","↗","cyan"],
        ["Saídas",currency(k.expenses),"Despesas pagas","↘","pink"],
        ["Saldo do período",currency(k.cashBalance),"Entradas − saídas","◈",""],
        ["Contas pendentes",integer(d.pending.length),"Compromissos simulados","◫","amber"]
      ])+
      section("Fluxo de caixa","Comparativo mensal")+
      '<div class="grid-2">'+
        panel("Entradas x saídas","Movimentação mensal",lineChart(d.months,[{key:"income",label:"Entradas",color:COLORS[1]},{key:"expense",label:"Saídas",color:COLORS[2]}],"Entradas e saídas"),"MENSAL")+
        panel("Despesas por categoria","Distribuição dos gastos",donut(d.expenseCategories,"Despesas","currency"),"DESPESAS")+
      '</div>'+
      section("Planejamento financeiro","Compromissos e categorias")+
      '<div class="grid-2 grid-even">'+
        panel("Maiores centros de custo","Gastos por categoria",barList(d.expenseCategories,"value","currency","amber"),"CATEGORIAS")+
        panel("Próximos vencimentos","Contas fictícias pendentes",table(["DESCRIÇÃO","VENCIMENTO","VALOR"],d.pending.map(r=>'<tr><td class="table-primary">'+esc(r.name)+'</td><td>'+esc(formatDate(r.due))+'</td><td>'+esc(currency(r.amount))+'</td></tr>')),"PENDENTES")+
      '</div>'+note;
  }
  function hr(d) {
    const k=d.kpis;
    return hero("PESSOAS / CULTURA","Pessoas são o diferencial.","Uma visão analítica da estrutura organizacional e da equipe.","PEOPLE ANALYTICS")+
      section("Indicadores de pessoas","Quadro atual — não filtrado pelo período")+
      metrics([
        ["Colaboradores ativos",integer(k.headcount),"Total da equipe","♧",""],
        ["Folha mensal",currency(k.payroll),"Estimativa salarial","◈","cyan"],
        ["Departamentos",integer(k.departments),"Áreas da empresa","▦","amber"],
        ["Média salarial",currency(k.payroll/k.headcount),"Folha ÷ colaboradores","◇","pink"]
      ])+
      section("Estrutura organizacional","Distribuição da equipe")+
      '<div class="grid-2">'+
        panel("Headcount por área","Número de colaboradores",barList(d.departments,"headcount","count"),"EQUIPE")+
        panel("Distribuição da equipe","Participação por departamento",donut(d.departments.map(r=>({name:r.name,value:r.headcount})),"Pessoas","count"),"HEADCOUNT")+
      '</div>'+
      section("Gestão de talentos","Custo e movimentação")+
      '<div class="grid-2">'+
        panel("Folha salarial por área","Custo mensal por departamento",barList(d.departments,"payroll","currency","cyan"),"FOLHA")+
        panel("Admissões e desligamentos","Movimentação sintética por mês",lineChart(d.hrMovements.map(r=>({label:r.label,hired:r.hired,left:r.left})),[{key:"hired",label:"Admissões",color:COLORS[1]},{key:"left",label:"Desligamentos",color:COLORS[3]}],"Admissões e desligamentos"),"MOVIMENTAÇÕES")+
      '</div>'+note;
  }
  function powerbi(d) {
    return hero("BI / INTEGRAÇÕES","Dados que viram decisões.","Um ecossistema de análise: SQL, Python, Streamlit e Power BI.","DATA PIPELINE")+
      section("Ecossistema de dados","Arquitetura do projeto")+
      '<div class="pb-feature"><div><div class="hero-tag">POWER BI + POSTGRESQL</div><h2>Do banco ao dashboard.</h2><p>O repositório inclui consultas SQL, processamento em Python/Pandas e exportação CSV para Power BI Desktop. Esta versão pública da Vercel usa dados sintéticos e não se conecta ao PostgreSQL de produção.</p><a class="link-button" href="https://github.com/jmrzd/Enterprise-Analytics-Dashboard/tree/main/powerbi" target="_blank" rel="noopener noreferrer">Ver documentação Power BI ↗</a></div><div class="pb-icon">▥</div></div>'+
      section("Fluxo de trabalho","Três etapas da integração")+
      '<div class="steps">'+
        '<div class="step"><span class="num">01 / DADOS</span><h3>PostgreSQL + SQL</h3><p>Banco relacional com vendas, produtos, clientes, lançamentos financeiros e departamentos. Scripts de criação e dados de teste no GitHub.</p></div>'+
        '<div class="step"><span class="num">02 / TRANSFORMAÇÃO</span><h3>Python + Pandas</h3><p>Consultas, indicadores e exportação de arquivos CSV agregados, organizados por módulo de negócio.</p></div>'+
        '<div class="step"><span class="num">03 / VISUALIZAÇÃO</span><h3>Power BI Desktop</h3><p>Importação dos dados para desenvolver relatórios de Vendas, Financeiro e RH. Arquivo PBIX ainda não publicado.</p></div>'+
      '</div>'+
      section("Dados para análise","Prévia de indicadores do período")+
      panel("Indicadores mensais","Receita, lucro e movimentações",table(["MÊS","RECEITA","LUCRO BRUTO","ENTRADAS","SAÍDAS"],d.months.map(r=>'<tr><td class="table-primary">'+esc(r.label)+'</td><td>'+esc(currency(r.revenue))+'</td><td>'+esc(currency(r.profit))+'</td><td>'+esc(currency(r.income))+'</td><td>'+esc(currency(r.expense))+'</td></tr>')),"DADOS SINTÉTICOS")+
      '<div class="callout"><strong>Próxima evolução:</strong> criar e versionar um relatório .pbix real, além de preparar conexão segura com PostgreSQL para uso interno. A demonstração pública não contém dados empresariais.</div>';
  }
  function render() {
    const d=state.data;
    if(!d)return;
    const view=state.view, v=VIEWS[view];
    $("pageTitle").innerHTML=esc(v[0])+' <span class="heading-star">✦</span>';
    $("pageSubtitle").textContent=v[1];
    $("crumbName").textContent=v[0];
    document.title=v[0]+" | Enterprise Analytics";
    document.querySelectorAll("[data-view]").forEach(btn=>{
      const active=btn.dataset.view===view;
      btn.classList.toggle("active",active);
      if(active)btn.setAttribute("aria-current","page");
      else btn.removeAttribute("aria-current");
    });
    $("dashboardContent").innerHTML=({overview,sales,finance,hr,powerbi})[view](d);
  }
  async function load() {
    const id=++state.request;
    $("message").innerHTML="";
    $("dashboardContent").innerHTML='<div class="loading"><div class="loader"></div><p>Atualizando indicadores...</p></div>';
    $("refreshBtn").disabled=true;
    try {
      const response=await fetch("/api/dashboard?period="+encodeURIComponent(state.period),{headers:{"Accept":"application/json"},cache:"no-store"});
      if(!response.ok)throw new Error("HTTP "+response.status);
      const data=await response.json();
      if(id!==state.request)return;
      if(!data.meta||data.meta.mode!=="demo")throw new Error("Resposta de dados inesperada");
      state.data=data;
      render();
    } catch(error) {
      if(id!==state.request)return;
      $("dashboardContent").innerHTML='<div class="error"><strong>Não foi possível carregar o dashboard.</strong><br>Verifique sua conexão e clique em atualizar. Detalhes: '+esc(error.message)+'</div>';
    } finally {if(id===state.request)$("refreshBtn").disabled=false;}
  }
  function exportCsv() {
    if(!state.data)return;
    const d=state.data;
    const configs={
      overview:[d.months,["label","revenue","profit","orders","income","expense"]],
      sales:[d.products,["name","units","revenue"]],
      finance:[d.months,["label","income","expense"]],
      hr:[d.departments,["name","headcount","payroll"]],
      powerbi:[d.months,["label","revenue","profit","orders","income","expense"]]
    };
    const config=configs[state.view],rows=config[0],cols=config[1];
    const csv=[cols.join(";")].concat(rows.map(row=>cols.map(k=>'"'+String(row[k]??"").replace(/"/g,'""')+'"').join(";"))).join("\r\n");
    const blob=new Blob(["\ufeff"+csv],{type:"text/csv;charset=utf-8"});
    const url=URL.createObjectURL(blob);
    const link=document.createElement("a");
    link.href=url;link.download="enterprise-analytics-"+state.view+"-"+state.period+".csv";
    document.body.appendChild(link);link.click();link.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    $("message").innerHTML='<div class="toast">✓ CSV de demonstração exportado com sucesso.</div>';
    setTimeout(()=>$("message").replaceChildren(),3500);
  }
  function closeMenu() {$("sidebar").classList.remove("open");$("mobileOverlay").hidden=true;}
  document.querySelectorAll("[data-view]").forEach(btn=>btn.addEventListener("click",()=>{
    state.view=btn.dataset.view;render();closeMenu();window.scrollTo({top:0,behavior:"smooth"});
  }));
  $("periodSelect").addEventListener("change",(e)=>{state.period=e.target.value;load();});
  $("refreshBtn").addEventListener("click",load);
  $("exportBtn").addEventListener("click",exportCsv);
  $("menuToggle").addEventListener("click",()=>{$("sidebar").classList.toggle("open");$("mobileOverlay").hidden=!$("sidebar").classList.contains("open");});
  $("mobileOverlay").addEventListener("click",closeMenu);
  document.addEventListener("keydown",(e)=>{if(e.key==="Escape")closeMenu();});
  $("topDate").textContent=new Intl.DateTimeFormat("pt-BR",{day:"2-digit",month:"short",year:"numeric"}).format(new Date());
  $("year").textContent=new Date().getFullYear();
  load();
})();