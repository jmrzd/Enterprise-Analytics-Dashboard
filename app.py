import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.analytics.vendas import resumo_vendas, produtos_mais_vendidos
from src.analytics.financeiro import fluxo_caixa, contas_pendentes
from src.analytics.rh import quadro_funcionarios, movimentacoes

st.set_page_config(page_title="Enterprise Analytics",page_icon="📊",layout="wide")
st.markdown("""
<style>
[data-testid="stApp"]{background:radial-gradient(ellipse at top right,#201a38,#0c101a 50%);color:#f0f2fa}
[data-testid="stSidebar"]{background:#121624;border-right:1px solid #2b3041}
.block-container{max-width:1450px;padding-top:2rem}
h1,h2,h3{letter-spacing:-.035em}
[data-testid="stMetric"]{background:linear-gradient(140deg,#1b2131,#151a27);border:1px solid #30364a;border-radius:16px;padding:18px}
[data-testid="stMetricLabel"]{color:#a7b1c7}
[data-testid="stMetricValue"]{font-size:1.8rem}
[data-testid="stPlotlyChart"]{border:1px solid #2d3446;background:#151a27;border-radius:16px;padding:8px}
[data-testid="stDataFrame"]{border-radius:12px;overflow:hidden}
</style>
""",unsafe_allow_html=True)

PURPLE="#a88aff"
TEAL="#45d9c5"
AMBER="#f5be74"
BG="#151a27"

def money(x):
    return f"R$ {float(x):,.2f}".replace(",","X").replace(".",",").replace("X",".")

def chart(fig):
    fig.update_layout(paper_bgcolor=BG,plot_bgcolor=BG,font=dict(color="#dce2f1"),
        margin=dict(l=15,r=15,t=45,b=20),height=345,
        xaxis=dict(showgrid=False),yaxis=dict(gridcolor="#2b3142"),
        legend=dict(orientation="h",y=1.16))
    st.plotly_chart(fig,width="stretch",config={"displaylogo":False})

def bars(frame,x,series,title):
    fig=go.Figure()
    for col,label,color in series:
        fig.add_bar(x=frame[x],y=frame[col],name=label,marker_color=color)
    fig.update_layout(title=title,barmode="group")
    chart(fig)

def lines(frame,x,series,title):
    fig=go.Figure()
    for col,label,color in series:
        fig.add_scatter(x=frame[x],y=frame[col],name=label,mode="lines+markers",
            line=dict(color=color,width=3),marker=dict(size=7))
    fig.update_layout(title=title)
    chart(fig)

def total(frame,col):
    return float(frame[col].sum()) if col in frame else 0.0

@st.cache_data(ttl=300)
def load():
    return resumo_vendas(),produtos_mais_vendidos(),fluxo_caixa(),contas_pendentes(),quadro_funcionarios(),movimentacoes()

with st.sidebar:
    st.markdown("## ◈ Enterprise Analytics")
    st.caption("BUSINESS INTELLIGENCE PLATFORM")
    st.divider()
    area=st.radio("Módulos",["Visão geral","Vendas","Financeiro","Recursos Humanos"])
    st.divider()
    st.caption("● PostgreSQL conectado via Python")
    st.caption("● Demonstração com dados fictícios")

try:
    vendas_all,produtos,fluxo_all,pendentes,rh,movimentos_all=load()
except Exception:
    st.error("Não foi possível consultar o PostgreSQL. Verifique Docker e DATABASE_URL.")
    st.stop()

years=set()
for df in (vendas_all,fluxo_all):
    if not df.empty:
        years.update(pd.to_datetime(df["mes"]).dt.year.astype(int).tolist())
with st.sidebar:
    year=st.selectbox("Ano",["Todos"]+[str(y) for y in sorted(years,reverse=True)])
    if st.button("↻ Atualizar dados",width="stretch"):
        load.clear()
        st.rerun()

def filtered(df):
    if year=="Todos" or df.empty:
        return df
    return df.loc[pd.to_datetime(df["mes"]).dt.year.eq(int(year))].copy()

vendas=filtered(vendas_all)
fluxo=filtered(fluxo_all)
receita=total(vendas,"receita")
lucro=total(vendas,"lucro_bruto")
saldo=total(fluxo,"saldo")
ativos=int(total(rh,"ativos"))

st.caption("ENTERPRISE ANALYTICS  /  DASHBOARD")
st.title({"Visão geral":"Visão geral da empresa","Vendas":"Vendas & faturamento","Financeiro":"Gestão financeira","Recursos Humanos":"Recursos Humanos"}[area])
st.caption("Indicadores empresariais em tempo de consulta • Dados fictícios para portfólio")
st.write("")

if area=="Visão geral":
    a,b,c,d=st.columns(4)
    a.metric("Receita de vendas",money(receita))
    b.metric("Lucro bruto estimado",money(lucro))
    c.metric("Saldo de caixa",money(saldo))
    d.metric("Funcionários ativos",ativos)
    st.write("")
    left,right=st.columns([1.3,1],gap="medium")
    with left:
        st.subheader("Receita mensal")
        if not vendas.empty:
            lines(vendas,"mes",[("receita","Receita",PURPLE)],"Evolução das vendas")
        else: st.info("Sem vendas neste período.")
    with right:
        st.subheader("Fluxo de caixa")
        if not fluxo.empty:
            bars(fluxo,"mes",[("entradas","Entradas",TEAL),("saidas","Saídas",AMBER)],"Entradas e saídas")
        else: st.info("Sem lançamentos neste período.")
    st.subheader("Equipe por departamento")
    if not rh.empty:
        fig=go.Figure(go.Pie(labels=rh["departamento"],values=rh["ativos"],hole=.66,
            marker=dict(colors=[PURPLE,TEAL,AMBER,"#7696ff"])))
        fig.update_layout(title="Distribuição dos colaboradores",showlegend=True)
        chart(fig)
    st.info("Receita de vendas, caixa e folha salarial são indicadores distintos. O saldo de caixa não é lucro líquido.")

elif area=="Vendas":
    a,b,c,d=st.columns(4)
    a.metric("Faturamento",money(receita))
    b.metric("Lucro bruto",money(lucro))
    c.metric("Pedidos concluídos",int(total(vendas,"pedidos")))
    d.metric("Margem bruta",f"{100*lucro/receita if receita else 0:.1f}%")
    st.subheader("Performance comercial")
    if not vendas.empty:
        bars(vendas,"mes",[("receita","Receita",PURPLE),("lucro_bruto","Lucro bruto",TEAL)],"Receita x lucro bruto")
    else: st.info("Sem vendas neste período.")
    st.subheader("Produtos mais vendidos (histórico completo)")
    if not produtos.empty:
        fig=go.Figure(go.Bar(y=produtos["produto"],x=produtos["unidades"],orientation="h",marker_color=PURPLE))
        fig.update_layout(title="Unidades vendidas",yaxis=dict(autorange="reversed"))
        chart(fig)
    st.dataframe(produtos,width="stretch",hide_index=True)
    st.download_button("↓ Exportar vendas CSV",vendas.to_csv(index=False).encode("utf-8-sig"),"vendas.csv","text/csv")

elif area=="Financeiro":
    a,b,c,d=st.columns(4)
    a.metric("Entradas",money(total(fluxo,"entradas")))
    b.metric("Saídas",money(total(fluxo,"saidas")))
    c.metric("Saldo",money(saldo))
    d.metric("Contas pendentes",len(pendentes))
    st.subheader("Fluxo financeiro")
    if not fluxo.empty:
        lines(fluxo,"mes",[("entradas","Entradas",TEAL),("saidas","Saídas",AMBER)],"Entradas x saídas pagas")
        bars(fluxo,"mes",[("saldo","Saldo",PURPLE)],"Saldo por mês")
    else: st.info("Sem movimentações neste período.")
    st.subheader("Contas pendentes (todos os períodos)")
    st.dataframe(pendentes,width="stretch",hide_index=True)
    st.download_button("↓ Exportar fluxo CSV",fluxo.to_csv(index=False).encode("utf-8-sig"),"fluxo.csv","text/csv")

else:
    a,b,c=st.columns(3)
    a.metric("Colaboradores ativos",ativos)
    b.metric("Folha mensal",money(total(rh,"folha_mensal")))
    c.metric("Departamentos",len(rh))
    left,right=st.columns(2)
    with left:
        st.subheader("Equipe por área")
        fig=go.Figure(go.Bar(y=rh["departamento"],x=rh["ativos"],orientation="h",marker_color=PURPLE))
        fig.update_layout(title="Funcionários ativos")
        chart(fig)
    with right:
        st.subheader("Folha por área")
        fig=go.Figure(go.Bar(x=rh["departamento"],y=rh["folha_mensal"],marker_color=TEAL))
        fig.update_layout(title="Salários mensais")
        chart(fig)
    st.dataframe(rh,width="stretch",hide_index=True)
    st.subheader("Admissões e desligamentos (histórico completo)")
    st.dataframe(movimentos_all,width="stretch",hide_index=True)
    st.caption("Quadro de funcionários e folha salarial representam a situação atual.")

st.divider()
st.caption("Enterprise Analytics • Python + PostgreSQL + Pandas + Plotly + Power BI • MVP de portfólio")
