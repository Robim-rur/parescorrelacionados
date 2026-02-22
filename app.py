import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="L&S Pro - Gestor de Sábado", layout="wide")

st.title("📊 Scanner e Gestor Long & Short (R$ 1.000,00)")

# --- LISTA DE PARES ---
PARES = [
    ("ITUB4.SA", "BBAS3.SA"), ("ITSA4.SA", "ITUB4.SA"),
    ("PETR4.SA", "PETR3.SA"), ("VALE3.SA", "GGBR4.SA"),
    ("ELET3.SA", "CPLE6.SA"), ("EQTL3.SA", "SBSP3.SA"),
    ("VIVT3.SA", "TIMS3.SA"), ("B3SA3.SA", "ITUB4.SA"),
    ("RENT3.SA", "LREN3.SA"), ("CSNA3.SA", "USIM5.SA")
]

def calcular_dados_completos():
    resultados = []
    capital_por_ponta = 500.00 # Divide R$ 1000 em duas partes
    
    for t1, t2 in PARES:
        try:
            df = yf.download([t1, t2], period="60d", progress=False)['Close']
            p1, p2 = df[t1].iloc[-1], df[t2].iloc[-1] # Preços atuais
            
            ratio = df[t1] / df[t2]
            z_score = (ratio.iloc[-1] - ratio.mean()) / ratio.std()
            
            # Cálculo de Quantidades (Arredondado para baixo para segurança)
            qtd_t1 = int(capital_por_ponta / p1)
            qtd_t2 = int(capital_por_ponta / p2)
            
            if z_score < 0:
                comando = f"COMPRE {qtd_t1} {t1} / VENDA {qtd_t2} {t2}"
            else:
                comando = f"VENDA {qtd_t1} {t1} / COMPRA {qtd_t2} {t2}"
                
            resultados.append({
                "Par": f"{t1} x {t2}",
                "Z-Score": round(z_score, 2),
                "Operação Sugerida": comando,
                "Financeiro Estimado": f"R$ {round((qtd_t1*p1) + (qtd_t2*p2), 2)}",
                "Abs": abs(z_score)
            })
        except: continue
    return resultados

# --- SECÇÃO 1: BUSCADOR ---
st.header("🔍 1. Scanner de Sábado (Novas Entradas)")
if st.button('Escanear Mercado'):
    dados = calcular_dados_completos()
    df_res = pd.DataFrame(dados).sort_values(by="Abs", ascending=False)
    
    # Exibe a tabela organizada
    st.table(df_res[["Par", "Z-Score", "Operação Sugerida", "Financeiro Estimado"]])

st.divider()

# --- SECÇÃO 2: MONITOR ---
st.header("🏁 2. Monitorizar Minha Operação Aberta")
par_aberto = st.selectbox("Qual par você já abriu?", [f"{p[0]} x {p[1]}" for p in PARES])

if st.button('Verificar Momento de Saída'):
    t1_aberto, t2_aberto = par_aberto.split(" x ")
    df_mon = yf.download([t1_aberto, t2_aberto], period="60d", progress=False)['Close']
    ratio_mon = df_mon[t1_aberto] / df_mon[t2_aberto]
    zs_atual = (ratio_mon.iloc[-1] - ratio_mon.mean()) / ratio_mon.std()
    
    st.metric("Z-Score Atual", round(zs_atual, 2))
    
    if abs(zs_atual) <= 0.5:
        st.balloons()
        st.success("✅ ALVO ATINGIDO! Encerre as duas pontas na segunda-feira.")
    else:
        st.info("⏳ DISTORÇÃO AINDA ATIVA. Mantenha a posição.")
