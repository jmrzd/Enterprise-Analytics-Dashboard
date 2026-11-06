"""Gráficos Plotly do tema Neon Observatory. Não inventa dados."""
import pandas as pd
import plotly.graph_objects as go

PURPLE = "#a855f7"
CYAN = "#22d3ee"
PINK = "#f472b6"
YELLOW = "#facc15"
GREEN = "#34d399"
RED = "#fb7185"
COLORS = [CYAN, PURPLE, PINK, YELLOW, GREEN, "#818cf8", "#fb923c"]
PLOT = "#160f2c"

def base(fig, height=315):
    fig.update_layout(
        height=height, template=None, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#bcb0d8", size=11),
        margin=dict(l=20, r=20, t=38, b=18),
        legend=dict(orientation="h", x=0, y=1.16, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified",
        xaxis=dict(showgrid=False, showline=False, zeroline=False, tickfont=dict(color="#8477aa")),
        yaxis=dict(showgrid=True, gridcolor="rgba(145,112,217,.15)", zeroline=False,
                   tickfont=dict(color="#8477aa"), rangemode="tozero"),
    )
    return fig

def area(frame, x, series, *, height=320):
    fig=go.Figure()
    if frame.empty:
        return base(fig,height)
    for name, column, color in series:
        fig.add_trace(go.Scatter(x=frame[x],y=frame[column],mode="lines",
            line=dict(color=color,width=8),opacity=.09,showlegend=False,hoverinfo="skip"))
        fig.add_trace(go.Scatter(x=frame[x],y=frame[column],name=name,mode="lines+markers",
            line=dict(color=color,width=2.6,shape="spline",smoothing=.45),
            marker=dict(size=5,color=color,line=dict(width=1,color="#170c30")),
            fill="tozeroy" if len(series)==1 else None,
            fillcolor="rgba(168,85,247,.10)" if len(series)==1 else None,
            hovertemplate="%{x|%b/%Y}: R$ %{y:,.2f}<extra>"+name+"</extra>"))
    fig=base(fig,height)
    fig.update_xaxes(tickformat="%b/%y")
    return fig

def columns(frame, x, series, *, height=300, stacked=False, money=False):
    fig=go.Figure()
    for name,column,color in series:
        fig.add_trace(go.Bar(x=frame[x],y=frame[column],name=name,marker_color=color,
            marker_line_width=0,opacity=.94,hovertemplate="%{x}: %{y:,.2f}<extra>"+name+"</extra>"))
    fig=base(fig,height)
    fig.update_layout(barmode="stack" if stacked else "group", bargap=.32)
    if money:fig.update_yaxes(tickprefix="R$ ")
    if x=="mes":fig.update_xaxes(tickformat="%b/%y")
    return fig

def donut(frame, labels, values, *, height=305, center_label="COMPOSIÇÃO"):
    fig=go.Figure()
    if not frame.empty and frame[values].sum()>0:
        fig.add_trace(go.Pie(labels=frame[labels], values=frame[values],hole=.72,
            textinfo="none",sort=False,marker=dict(colors=COLORS,line=dict(color="#17102e",width=4)),
            hovertemplate="%{label}<br>%{percent}<extra></extra>"))
        fig.update_layout(annotations=[dict(text=center_label,x=.5,y=.5,showarrow=False,
             font=dict(size=12,color="#b8a9d8"))],showlegend=True,
             legend=dict(orientation="h",x=.5,xanchor="center",y=-.12,font=dict(size=10)))
    return base(fig,height)

def horizontal(frame, labels, values, *, height=310, color=PURPLE):
    fig=go.Figure()
    if not frame.empty:
        f=frame.sort_values(values,ascending=True).tail(8)
        fig.add_bar(x=f[values],y=f[labels],orientation="h",marker=dict(color=color,
            line=dict(width=0)),hovertemplate="%{y}: %{x:,.2f}<extra></extra>")
    fig=base(fig,height)
    fig.update_layout(showlegend=False)
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=True,gridcolor="rgba(145,112,217,.15)")
    return fig

def radar(frame, labels, values, *, height=320):
    fig=go.Figure()
    if not frame.empty and frame[values].sum()>0:
        f=frame[[labels,values]].copy()
        r=pd.to_numeric(f[values],errors="coerce").fillna(0).tolist()
        names=f[labels].astype(str).tolist()
        r.append(r[0]);names.append(names[0])
        fig.add_trace(go.Scatterpolar(r=r,theta=names,mode="lines+markers",fill="toself",
            name="Funcionários ativos",line=dict(color=PINK,width=2),
            marker=dict(color=CYAN,size=6),fillcolor="rgba(168,85,247,.23)"))
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True,showticklabels=False,gridcolor="rgba(145,112,217,.18)"),
            angularaxis=dict(gridcolor="rgba(145,112,217,.18)",tickfont=dict(color="#b8afd0",size=10))),
            showlegend=False)
    return base(fig,height)

def status(frame, *, height=240):
    return donut(frame,"status","total",height=height,center_label="PEDIDOS")
