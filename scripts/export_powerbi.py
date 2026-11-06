"""Exporta dados agregados de demonstração para CSV (sem dados pessoais)."""
from pathlib import Path

from src.analytics.vendas import resumo_vendas, produtos_mais_vendidos
from src.analytics.financeiro import fluxo_caixa
from src.analytics.rh import quadro_funcionarios

def main():
    folder=Path("outputs")
    folder.mkdir(exist_ok=True)
    for name,frame in {
        "vendas_mensais":resumo_vendas(),
        "produtos":produtos_mais_vendidos(),
        "fluxo_caixa":fluxo_caixa(),
        "rh_departamentos":quadro_funcionarios(),
    }.items():
        frame.to_csv(folder/f"{name}.csv",index=False)
        print(f"Exportado: {folder/name}.csv")

if __name__=="__main__":
    main()
