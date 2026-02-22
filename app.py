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
def calcular_zscore(t1, t2):
    df = yf.download([t1, t2], period="60d", progress=False)['Close']
    ratio = df[t1] / df[t2]
    z_score = (ratio.iloc[-1] - ratio.mean()) / ratio.std()
    return round(z_score, 2)

# --- SECÇÃO 1: BUSCADOR DE NOVAS OPORTUNIDADES ---
st.header("🔍 1. Encontrar Novas Operações (Sábado)")
if st.button('Escanear Mercado'):
    resultados = []
    for t1, t2 in PARES:
        try:
            zs = calcular_zscore(t1, t2)
            resultados.append({"Par": f"{t1} x {t2}", "Z-Score": zs, "Abs": abs(zs)})
        except: continue
    
    df_res = pd.DataFrame(resultados).sort_values(by="Abs", ascending=False)
    st.table(df_res[["Par", "Z-Score"]])

st.divider()

# --- SECÇÃO 2: MONITOR DE ENCERRAMENTO ---
st.header("🏁 2. Monitorizar Minha Operação Aberta")
st.write("Selecione o par que você abriu na semana anterior para ver se deve fechar.")

par_aberto = st.selectbox("Qual par você está operando?", [f"{p[0]} x {p[1]}" for p in PARES])

if st.button('Verificar Momento de Saída'):
    t1_aberto, t2_aberto = par_aberto.split(" x ")
    zs_atual = calcular_zscore(t1_aberto, t2_aberto)
    
    st.metric("Z-Score Atual", zs_atual)
    
    # LÓGICA DE DECISÃO DE FECHAMENTO
    if abs(zs_atual) <= 0.5:
        st.balloons()
        st.success("✅ HORA DE FECHAR! O Z-Score voltou para a média (perto de zero). Realize seu lucro na segunda-feira!")
    elif abs(zs_atual) >= 3.5:
        st.error("⚠️ ALERTA DE STOP! A distorção aumentou demais. Considere fechar para proteger seu capital.")
    else:
        st.info("⏳ MANTENHA A OPERAÇÃO. A distorção ainda não corrigiu o suficiente para o alvo.")

st.sidebar.markdown("""
### Regras do Ricardo Brasil:
- **Entrada:** Z-Score > 2.0 ou < -2.0
- **Saída (Alvo):** Z-Score entre -0.5 e 0.5
- **Stop:** Z-Score acima de 3.5 ou abaixo de -3.5
""")
