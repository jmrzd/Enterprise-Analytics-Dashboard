import streamlit as st
import pandas as pd
import plotly.express as px

from src.analytics.vendas import resumo_vendas, produtos_mais_vendidos
from src.analytics.financeiro import fluxo_caixa, contas_pendentes
from src.analytics.rh import quadro_funcionarios, movimentacoes

st.set_page_config(page_title="Enterprise Analytics",page_icon="📊",layout="wide")
st.title("📊 Enterprise Analytics Dashboard")
st.caption("Demonstração com dados fictícios • Vendas, Financeiro e RH")
area=st.sidebar.radio("Módulo",["Visão geral","Vendas","Financeiro","Recursos Humanos"])

@st.cache_data(ttl=300)
def load_data():
    return (resumo_vendas(),produtos_mais_vendidos(),fluxo_caixa(),
            contas_pendentes(),quadro_funcionarios(),movimentacoes())

def money(value):
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

try:
    vendas,produtos,fluxo,pendentes,rh,movimentos=load_data()
except Exception:
    st.error("Não foi possível consultar o banco. Confira o PostgreSQL e a variável DATABASE_URL.")
    st.stop()

if area=="Visão geral":
    a,b,c=st.columns(3)
    a.metric("Receita de vendas concluídas",money(vendas["receita"].sum()))
    b.metric("Saldo de caixa (lançamentos pagos)",money(fluxo["saldo"].sum()))
    c.metric("Funcionários ativos",int(rh["ativos"].sum()))
    st.info("Receita de vendas, lançamentos financeiros e folha salarial são indicadores distintos; não some os valores sem conciliação contábil.")
elif area=="Vendas":
    st.subheader("Vendas e faturamento")
    a,b=st.columns(2)
    a.metric("Receita",money(vendas["receita"].sum()))
    b.metric("Lucro bruto estimado",money(vendas["lucro_bruto"].sum()))
    if not vendas.empty:
        st.plotly_chart(px.bar(vendas,x="mes",y="receita",title="Receita por mês"),use_container_width=True)
    st.dataframe(produtos,use_container_width=True,hide_index=True)
elif area=="Financeiro":
    st.subheader("Financeiro e fluxo de caixa")
    st.metric("Saldo de caixa",money(fluxo["saldo"].sum()))
    if not fluxo.empty:
        st.plotly_chart(px.line(fluxo,x="mes",y=["entradas","saidas"],title="Entradas e saídas pagas"),use_container_width=True)
    st.write("Contas pendentes")
    st.dataframe(pendentes,use_container_width=True,hide_index=True)
else:
    st.subheader("Recursos Humanos")
    st.metric("Colaboradores ativos",int(rh["ativos"].sum()))
    st.metric("Folha salarial mensal (ativos)",money(rh["folha_mensal"].sum()))
    st.dataframe(rh,use_container_width=True,hide_index=True)
    st.write("Movimentações")
    st.dataframe(movimentos,use_container_width=True,hide_index=True)
