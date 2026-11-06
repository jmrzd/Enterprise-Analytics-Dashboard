"""Enterprise Analytics — Neon Observatory.
Dashboard empresarial: PostgreSQL local ou dados sintéticos na vitrine pública.
"""
import os
from datetime import date
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics.insights import (
    clientes_diarios, lancamentos_pagos, lancamentos_pendentes,
    produtos_diarios, status_pedidos, vendas_diarias,
)
from src.analytics.rh import movimentacoes, quadro_funcionarios
from src.demo_data import load_demo_data
from src.charts import CYAN, GREEN, PINK, PURPLE, YELLOW, area, columns, donut, horizontal, radar
from src.metrics import (
    amount, brl, cash_summary, compact_brl, filter_period,
    group_sum, monthly, pct, period_bounds,
)

DEMO_MODE = os.environ.get("DEMO_MODE", "").strip().lower() in {"1", "true", "yes", "on"}

st.set_page_config(page_title="Enterprise Analytics • BI", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>" + (Path(__file__).parent / "assets/dashboard.css").read_text(encoding="utf-8") + "</style>",
            unsafe_allow_html=True)

@st.cache_data(ttl=300, show_spinner=False)
def fetch_data():
    """Cache expira em cinco minutos; demo não utiliza banco de dados."""
    if DEMO_MODE:
        return load_demo_data()
    return {
        "sales": vendas_diarias(),
        "products": produtos_diarios(),
        "clients": clientes_diarios(),
        "orders": status_pedidos(),
        "cash": lancamentos_pagos(),
        "pending": lancamentos_pendentes(),
        "hr": quadro_funcionarios(),
        "movements": movimentacoes(),
    }


def metric(title, value, icon, color, foot):
    """Apenas strings estáticas ou métricas formatadas são inseridas neste HTML."""
    st.markdown(
        f'<div class="ea-kpi" style="--accent:{color}">'
        f'<div class="ea-kpi-title">{escape(title)}<span class="ea-kpi-icon">{escape(icon)}</span></div>'
        f'<div class="ea-kpi-value">{escape(str(value))}</div>'
        f'<div class="ea-kpi-foot">{escape(foot)}</div></div>',
        unsafe_allow_html=True,
    )


def hero(title, accent, description, period_label):
    st.markdown(
        '<div class="ea-hero">'
        '<div class="ea-eyebrow">◈ &nbsp; ENTERPRISE / BUSINESS INTELLIGENCE</div>'
        f'<div class="ea-hero-title">{escape(title)} <em>{escape(accent)}</em></div>'
        f'<div class="ea-hero-desc">{escape(description)}</div>'
        f'<div class="ea-hero-tag">✦ DADOS DEMONSTRATIVOS &nbsp; · &nbsp; {escape(period_label)}</div>'
        '</div>', unsafe_allow_html=True,
    )


def section(title, description="", pill="ANÁLISE"):
    st.markdown(
        '<div class="ea-section"><div>'
        f'<div class="ea-section-title">{escape(title)}</div>'
        f'<div class="ea-section-sub">{escape(description)}</div></div>'
        f'<div class="ea-section-pill">{escape(pill)}</div></div>',
        unsafe_allow_html=True,
    )


def graph(fig, key):
    st.plotly_chart(fig, width="stretch", theme=None,
                    config={"displaylogo": False, "responsive": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
                    key=key)


def notice(message):
    st.markdown(f'<div class="ea-empty">◈ &nbsp; {escape(message)}</div>', unsafe_allow_html=True)


def download_csv(label, df, filename):
    st.download_button(label, data=df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=filename, mime="text/csv", disabled=df.empty, key=filename)


def cash_months(frame):
    if frame.empty:
        return pd.DataFrame(columns=["mes", "entradas", "saidas", "saldo"])
    data=frame.copy()
    values=pd.to_numeric(data["valor"],errors="coerce").fillna(0)
    data["entradas"]=values.where(data["tipo"].eq("receita"),0)
    data["saidas"]=values.where(data["tipo"].eq("despesa"),0)
    result=monthly(data,["entradas","saidas"])
    result["saldo"]=result["entradas"]-result["saidas"]
    return result


with st.sidebar:
    st.markdown(
        '<div class="ea-brand"><span class="ea-brand-mark">◈</span>'
        '<div><div class="ea-brand-main">Enterprise <em>Analytics</em></div>'
        '<div class="ea-brand-sub">DATA INTELLIGENCE</div></div></div>', unsafe_allow_html=True,
    )
    st.markdown('<div class="ea-sidebar-label">WORKSPACE</div>', unsafe_allow_html=True)
    selected=st.radio("Navegação",[
        "◈  Visão geral", "↗  Vendas", "▤  Financeiro",
        "♧  Recursos Humanos", "▦  Power BI"
    ], label_visibility="collapsed")
    st.divider()
    st.markdown('<div class="ea-sidebar-label">FILTROS</div>', unsafe_allow_html=True)

try:
    with st.spinner("Carregando dados sintéticos..." if DEMO_MODE else "Consultando o PostgreSQL..."): 
        data=fetch_data()
except Exception:
    if DEMO_MODE:
        st.error("Falha ao carregar os dados da demonstração. Verifique os testes e logs.")
    else:
        st.error("Não foi possível acessar o PostgreSQL. Verifique o Docker e a variável DATABASE_URL no arquivo .env.")
        st.code("docker compose up -d\npython -m streamlit run app.py",language="bash")
    st.stop()

sources=[f for k,f in data.items() if k in ("sales","cash","orders") and not f.empty]
dates=[pd.to_datetime(f["data"],errors="coerce") for f in sources]
if dates and any(x.notna().any() for x in dates):
    first=min(x.min().date() for x in dates if x.notna().any())
    latest=max(x.max().date() for x in dates if x.notna().any())
else:
    first=latest=date.today()

with st.sidebar:
    preset=st.selectbox("Janela de análise",["Todo o histórico","30 dias","90 dias","180 dias","365 dias","Personalizado"],index=0)
    if preset=="Personalizado":
        start=st.date_input("De",value=first,min_value=first,max_value=latest)
        end=st.date_input("Até",value=latest,min_value=first,max_value=latest)
        if start>end:
            st.warning("A data inicial não pode ser posterior à final.")
            st.stop()
    else:
        start,end=period_bounds(latest,preset,first)
    if st.button("↻ Recarregar dados" if DEMO_MODE else "↻ Atualizar banco",width="stretch"):
        fetch_data.clear()
        st.rerun()
    connection = (
        "<strong>Modo demonstração</strong><br>Fonte: dados sintéticos + Pandas<br>Sem conexão com PostgreSQL"
        if DEMO_MODE else
        "<strong>PostgreSQL conectado</strong><br>Fonte: consultas SQL + Pandas"
    )
    st.markdown(
        f'<div class="ea-connection"><span class="ea-dot"></span>{connection}<br>'
        f'Cache: até 5 minutos<br>Último registro: {latest:%d/%m/%Y}</div>',
        unsafe_allow_html=True,
    )
    st.caption("◈ Protótipo de portfólio · dados fictícios")

period_label=f"{start:%d/%m/%Y} → {end:%d/%m/%Y}"
filtered={k:filter_period(data[k],start,end) for k in ("sales","products","clients","orders","cash")}
sales=filtered["sales"]
products=filtered["products"]
clients=filtered["clients"]
orders=filtered["orders"]
cash=filtered["cash"]
pending=data["pending"]
hr=data["hr"]
movements=data["movements"]
ms=monthly(sales,["receita","lucro_bruto","pedidos"])
mc=cash_months(cash)
sums=cash_summary(cash)
revenue=amount(sales,"receita")
gross=amount(sales,"lucro_bruto")
sales_count=int(amount(sales,"pedidos"))
active=int(amount(hr,"ativos"))
payroll=amount(hr,"folha_mensal")
categories=group_sum(products,"categoria",["receita","unidades"])
top_products=group_sum(products,"produto",["unidades","receita","lucro_bruto"])
top_clients=group_sum(clients,"cliente",["receita"])
statuses=group_sum(orders,"status",["total"])
expenses=group_sum(cash.loc[cash["tipo"]=="despesa"],"categoria",["valor"]) if not cash.empty else pd.DataFrame(columns=["categoria","valor"])

if selected=="◈  Visão geral":
    hero("Observatório", "empresarial",
         "Dados transformados em decisões. Explore vendas, movimentações financeiras e pessoas em uma única visão.",
         period_label)
    a,b,c,d=st.columns(4,gap="medium")
    with a:metric("Receita de vendas",compact_brl(revenue),"↗",PURPLE,"Pedidos concluídos")
    with b:metric("Lucro bruto",compact_brl(gross),"◈",CYAN,f"Margem {pct(gross,revenue):.1f}%")
    with c:metric("Saldo de caixa",compact_brl(sums["saldo"]),"▥",GREEN,"Somente lançamentos pagos")
    with d:metric("Colaboradores ativos",active,"♧",PINK,"Posição atual, não histórica")
    section("Painel de performance","Tendências de receita e fluxo de caixa",pill="DADOS SINTÉTICOS → PANDAS" if DEMO_MODE else "POSTGRESQL → PYTHON")
    left,right=st.columns([1.35,1],gap="medium")
    with left:
        if not ms.empty:graph(area(ms,"mes",[("Receita","receita",PURPLE)],height=340),"overview_revenue")
        else:notice("Nenhuma venda concluída no período.")
    with right:
        if not mc.empty:graph(columns(mc,"mes",[("Entradas","entradas",CYAN),("Saídas","saidas",PINK)],height=340,money=True),"overview_cash")
        else:notice("Nenhuma movimentação paga no período.")
    section("Inteligência por segmento","Composição das vendas, equipe e volume semanal",pill="INSIGHTS")
    a,b,c=st.columns(3,gap="medium")
    with a:
        if not categories.empty:graph(donut(categories,"categoria","receita",center_label="VENDAS"),"overview_categories")
        else:notice("Sem vendas por categoria.")
    with b:
        if not hr.empty:graph(radar(hr,"departamento","ativos"),"overview_team")
        else:notice("Sem equipe cadastrada.")
    with c:
        if not sales.empty:
            weekly=sales.copy()
            weekly["semana"]=pd.to_datetime(weekly["data"]).dt.to_period("W").dt.start_time
            weekly=weekly.groupby("semana",as_index=False)["pedidos"].sum().tail(9)
            graph(columns(weekly,"semana",[("Pedidos","pedidos",CYAN)],height=315),"overview_weekly")
        else:notice("Sem volume semanal.")
    section("Principais clientes","Ranking por receita de pedidos concluídos",pill="TOP 5")
    if not top_clients.empty:
        graph(horizontal(top_clients.head(5),"cliente","receita",height=260,color=PURPLE),"overview_customers")
    else:notice("Nenhum cliente com vendas no período.")

elif selected=="↗  Vendas":
    hero("Vendas &", "faturamento",
         "Receita, rentabilidade bruta, produtos líderes e desempenho comercial sem números inventados.",
         period_label)
    a,b,c,d=st.columns(4)
    with a:metric("Receita de vendas",compact_brl(revenue),"↗",PURPLE,"Pedidos concluídos")
    with b:metric("Lucro bruto",compact_brl(gross),"◈",CYAN,"Receita − custo dos produtos")
    with c:metric("Pedidos",sales_count,"▤",PINK,"Somente concluídos")
    with d:metric("Margem bruta",f"{pct(gross,revenue):.1f}%","◎",GREEN,"Sem despesas operacionais")
    section("Crescimento de vendas","Receita e lucro bruto por mês",pill="EVOLUÇÃO")
    if not ms.empty:
        graph(area(ms,"mes",[("Receita","receita",PURPLE),("Lucro bruto","lucro_bruto",CYAN)],height=365),"sales_growth")
    else:notice("Nenhuma venda no intervalo selecionado.")
    left,right=st.columns([1.1,1],gap="medium")
    with left:
        section("Produtos mais vendidos","Unidades vendidas por produto",pill="RANKING")
        if not top_products.empty:graph(horizontal(top_products,"produto","unidades",height=330,color=CYAN),"sales_items")
        else:notice("Sem produtos vendidos.")
    with right:
        section("Mix de faturamento","Participação da receita por categoria",pill="COMPOSIÇÃO")
        if not categories.empty:graph(donut(categories,"categoria","receita",height=330,center_label="RECEITA"),"sales_mix")
        else:notice("Sem categorias no período.")
    left,right=st.columns([1,1])
    with left:
        section("Status de pedidos","Inclui pendentes e cancelados",pill="QUALIDADE")
        if not statuses.empty:graph(donut(statuses,"status","total",height=300,center_label="PEDIDOS"),"sales_status")
        else:notice("Não há pedidos neste período.")
    with right:
        section("Carteira de clientes","Receita agregada por cliente",pill="CLIENTES")
        if not top_clients.empty:graph(horizontal(top_clients.head(6),"cliente","receita",height=300,color=PINK),"sales_clients")
        else:notice("Não há clientes no intervalo.")
    section("Detalhamento comercial","Resultados agregados para análise e exportação",pill="CSV")
    st.dataframe(top_products.rename(columns={"produto":"Produto","unidades":"Unidades","receita":"Receita (R$)","lucro_bruto":"Lucro bruto (R$)"}),
                 hide_index=True,width="stretch")
    download_csv("↓ Exportar vendas por dia",sales,"vendas_periodo.csv")

elif selected=="▤  Financeiro":
    hero("Gestão", "financeira",
         "Acompanhe entradas, despesas, fluxo de caixa e categorias de gastos efetivamente pagos.",
         period_label)
    a,b,c,d=st.columns(4)
    with a:metric("Entradas pagas",compact_brl(sums["entradas"]),"↗",CYAN,"Lançamentos realizados")
    with b:metric("Despesas pagas",compact_brl(sums["saidas"]),"↘",PINK,"Lançamentos realizados")
    with c:metric("Saldo do período",compact_brl(sums["saldo"]),"◈",GREEN,"Entradas − saídas")
    with d:metric("Contas pendentes",len(pending),"▤",YELLOW,"Todas as datas de vencimento")
    section("Fluxo de caixa","Entradas e saídas por mês",pill="MOVIMENTAÇÕES")
    if not mc.empty:graph(area(mc,"mes",[("Entradas","entradas",CYAN),("Saídas","saidas",PINK)],height=370),"fin_flow")
    else:notice("Nenhum lançamento pago neste período.")
    left,right=st.columns(2,gap="medium")
    with left:
        section("Despesas por categoria","Onde se concentram os pagamentos",pill="COMPOSIÇÃO")
        if not expenses.empty:graph(donut(expenses,"categoria","valor",height=325,center_label="DESPESAS"),"fin_expenses")
        else:notice("Nenhuma despesa paga no intervalo.")
    with right:
        section("Saldo acumulado","Acúmulo dentro do período selecionado",pill="TENDÊNCIA")
        if not mc.empty:
            cumulative=mc[["mes","saldo"]].copy()
            cumulative["acumulado"]=pd.to_numeric(cumulative["saldo"]).cumsum()
            graph(area(cumulative,"mes",[("Saldo acumulado","acumulado",PURPLE)],height=325),"fin_balance")
        else:notice("Sem saldo para visualizar.")
    section("Contas em aberto","Todas as pendências registradas, independentemente do filtro",pill="PENDÊNCIAS")
    st.dataframe(pending.rename(columns={"descricao":"Descrição","categoria":"Categoria","tipo":"Tipo","valor":"Valor (R$)","data_vencimento":"Vencimento"}),
                 width="stretch",hide_index=True)
    download_csv("↓ Exportar movimentações pagas",cash,"financeiro_periodo.csv")
    st.markdown('<div class="ea-pane-intro"><strong>Nota contábil:</strong> os lançamentos financeiros do MVP são independentes dos pedidos e da folha. Saldo de caixa não equivale ao lucro líquido.</div>',unsafe_allow_html=True)

elif selected=="♧  Recursos Humanos":
    hero("People", "analytics",
         "Distribuição de equipes, custo salarial, admissões e desligamentos para uma visão clara de RH.",
         "Quadro atual · movimentações históricas")
    a,b,c,d=st.columns(4)
    with a:metric("Equipe ativa",active,"♧",PURPLE,"Colaboradores não desligados")
    with b:metric("Folha mensal",compact_brl(payroll),"◈",CYAN,"Soma dos salários dos ativos")
    with c:metric("Departamentos",len(hr),"▥",PINK,"Áreas cadastradas")
    with d:metric("Salário médio",compact_brl(payroll/active if active else 0),"◎",GREEN,"Média dos colaboradores ativos")
    section("Estrutura organizacional","Distribuição atual por departamento",pill="HEADCOUNT")
    left,right=st.columns(2,gap="medium")
    with left:
        if not hr.empty:graph(radar(hr,"departamento","ativos",height=348),"hr_radar")
        else:notice("Sem dados da equipe.")
    with right:
        if not hr.empty:graph(horizontal(hr,"departamento","ativos",height=348,color=CYAN),"hr_departments")
        else:notice("Sem departamentos.")
    section("Custos e movimentações","Folha atual e histórico de entradas e saídas",pill="PESSOAS")
    left,right=st.columns(2,gap="medium")
    with left:
        if not hr.empty:graph(columns(hr,"departamento",[("Folha","folha_mensal",PURPLE)],height=330,money=True),"hr_payroll")
        else:notice("Sem folha cadastrada.")
    with right:
        if not movements.empty:
            move=movements.copy()
            move["mes"]=pd.to_datetime(move["mes"])
            move["quantidade"]=pd.to_numeric(move["quantidade"],errors="coerce")
            wide=move.pivot_table(index="mes",columns="movimento",values="quantidade",aggfunc="sum",fill_value=0).reset_index()
            for col in ("admissao","desligamento"):
                if col not in wide:wide[col]=0
            graph(columns(wide,"mes",[("Admissões","admissao",CYAN),("Desligamentos","desligamento",PINK)],height=330),"hr_moves")
        else:notice("Sem movimentações históricas.")
    section("Quadro de pessoal","Números agregados, sem divulgar dados individuais",pill="TABELA")
    st.dataframe(hr.rename(columns={"departamento":"Departamento","ativos":"Ativos","folha_mensal":"Folha mensal (R$)"}),
                 width="stretch",hide_index=True)
    st.markdown('<div class="ea-pane-intro"><strong>Escopo:</strong> quadro e folha representam a situação atual; a movimentação de colaboradores é histórica, sem aplicar o filtro comercial.</div>',unsafe_allow_html=True)
    download_csv("↓ Exportar indicadores agregados de RH",hr,"rh_departamentos.csv")

else:
    hero("Integração", "Power BI",
         "No modo local, o PostgreSQL alimenta a aplicação; a vitrine pública usa dados sintéticos.",
         "Exportação disponível")
    a,b,c=st.columns(3)
    with a:metric("Fontes",3,"◈",PURPLE,"Vendas, Financeiro e RH")
    with b:metric("Formato de saída","CSV","▤",CYAN,"Codificação UTF-8 com BOM")
    with c:metric("Dados","Agregados","◎",GREEN,"Somente ambiente fictício")
    section("Datasets prontos","Baixe indicadores filtrados ou use a conexão PostgreSQL",pill="EXPORTAR")
    a,b,c=st.columns(3)
    with a:download_csv("↓ Vendas mensais",ms,"powerbi_vendas.csv")
    with b:download_csv("↓ Fluxo financeiro",mc,"powerbi_financeiro.csv")
    with c:download_csv("↓ RH por departamento",hr,"powerbi_rh.csv")
    st.markdown("""
    <div class="ea-steps">
      <div class="ea-step"><strong>01 · Power BI Desktop</strong><br>Abra o Power BI Desktop e selecione <strong>Obter dados → Texto/CSV</strong> para importar os arquivos agregados exportados acima.</div>
      <div class="ea-step"><strong>02 · Conexão direta</strong><br>Como alternativa, use <strong>Obter dados → PostgreSQL</strong>, servidor <code>localhost:5432</code> e banco <code>enterprise_analytics</code>. Use somente credenciais do seu ambiente local.</div>
      <div class="ea-step"><strong>03 · Publicação</strong><br>Construa relatórios com receita, margem, saldo e headcount. Para compartilhar dados privados, configure autenticação, permissões, licenciamento e atualização de dados no Power BI Service.</div>
    </div>""",unsafe_allow_html=True)
    st.info("Um arquivo .pbix ainda não foi construído: esta página entrega as fontes e o roteiro de integração. Não publique dados de RH de pessoas reais.")

st.markdown(
    '<div class="ea-foot"><span>◈ ENTERPRISE ANALYTICS · FUTURISTIC BUSINESS INTELLIGENCE</span>'
    '<span>PYTHON · POSTGRESQL · PANDAS · PLOTLY · POWER BI &nbsp; | &nbsp; DEMO / PORTFÓLIO</span></div>',
    unsafe_allow_html=True,
)
