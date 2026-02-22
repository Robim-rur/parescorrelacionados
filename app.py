import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="L&S Pro - Gestor de Sábado", layout="wide")

st.title("📊 Scanner e Gestor Long & Short")

# --- LISTA DE PARES ---
PARES = [
    ("ITUB4.SA", "BBAS3.SA"), ("ITSA4.SA", "ITUB4.SA"),
    ("PETR4.SA", "PETR3.SA"), ("VALE3.SA", "GGBR4.SA"),
    ("ELET3.SA", "CPLE6.SA"), ("EQTL3.SA", "SBSP3.SA"),
    ("VIVT3.SA", "TIMS3.SA"), ("B3SA3.SA", "ITUB4.SA"),
    ("RENT3.SA", "LREN3.SA"), ("CSNA3.SA", "USIM5.SA")
]

# --- FUNÇÃO DE CÁLCULO ---
def calcular_dados_completos():
    resultados = []
    for t1, t2 in PARES:
        try:
            df = yf.download([t1, t2], period="60d", progress=False)['Close']
            ratio = df[t1] / df[t2]
            z_score = (ratio.iloc[-1] - ratio.mean()) / ratio.std()
            
            # Lógica das Palavras Compre e Venda
            if z_score < 0:
                comando = f"COMPRE {t1} / VENDA {t2}"
            else:
                comando = f"VENDA {t1} / COMPRA {t2}"
                
            resultados.append({
                "Par": f"{t1} x {t2}",
                "Z-Score": round(z_score, 2),
                "Operação Sugerida": comando,
                "Abs": abs(z_score)
            })
        except: continue
    return resultados

# --- SECÇÃO 1: BUSCADOR ---
st.header("🔍 1. Encontrar Novas Operações (Sábado)")
if st.button('Escanear Mercado'):
    dados = calcular_dados_completos()
    df_res = pd.DataFrame(dados).sort_values(by="Abs", ascending=False)
    
    # Exibindo a tabela com as palavras COMPRE e VENDA
    st.table(df_res[["Par", "Z-Score", "Operação Sugerida"]])

st.divider()

# --- SECÇÃO 2: MONITOR ---
st.header("🏁 2. Monitorizar Minha Operação Aberta")
par_aberto = st.selectbox("Qual par você está operando?", [f"{p[0]} x {p[1]}" for p in PARES])

if st.button('Verificar Momento de Saída'):
    t1_aberto, t2_aberto = par_aberto.split(" x ")
    # Recalcula apenas para o par selecionado
    df_mon = yf.download([t1_aberto, t2_aberto], period="60d", progress=False)['Close']
    ratio_mon = df_mon[t1_aberto] / df_mon[t2_aberto]
    zs_atual = (ratio_mon.iloc[-1] - ratio_mon.mean()) / ratio_mon.std()
    
    st.metric("Z-Score Atual", round(zs_atual, 2))
    
    if abs(zs_atual) <= 0.5:
        st.balloons()
        st.success("✅ HORA DE FECHAR! A distorção acabou. Realize seu lucro na segunda-feira!")
    else:
        st.info("⏳ MANTENHA A OPERAÇÃO. A distorção ainda não voltou para a média.")
