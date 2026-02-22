import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="L&S Pro - R. Brasil", layout="wide")

st.title("📊 Scanner de Alta Probabilidade - Long & Short")
st.write("Resultados ordenados pela maior distorção estatística (Z-Score).")

# 1. Lista Expandida de Pares Correlacionados
PARES = [
    ("ITUB4.SA", "BBAS3.SA"), ("ITSA4.SA", "ITUB4.SA"), # Bancos
    ("PETR4.SA", "PETR3.SA"), ("VALE3.SA", "GGBR4.SA"), # Commodities
    ("ELET3.SA", "CPLE6.SA"), ("EQTL3.SA", "SBSP3.SA"), # Utilidades
    ("VIVT3.SA", "TIMS3.SA"), # Telecom
    ("B3SA3.SA", "ITUB4.SA"), # Financeiro
    ("RENT3.SA", "LREN3.SA"), # Consumo/Serviços
    ("CSNA3.SA", "USIM5.SA")  # Siderurgia
]

def calcular_analise():
    dados_finais = []
    # Usamos 60 dias para ter uma média móvel sólida
    for t1, t2 in PARES:
        try:
            df = yf.download([t1, t2], period="60d", progress=False)['Close']
            ratio = df[t1] / df[t2]
            
            # Cálculo do Z-Score
            media = ratio.mean()
            desvio = ratio.std()
            z_score = (ratio.iloc[-1] - media) / desvio
            
            # Cálculo de quantidades para R$ 1.000 total (500 cada ponta)
            p1, p2 = df[t1].iloc[-1], df[t2].iloc[-1]
            qtd_a, qtd_b = int(500 / p1), int(500 / p2)
            
            dados_finais.append({
                "Par": f"{t1} x {t2}",
                "Z_Score_Abs": abs(z_score), # Para ordenação
                "Z_Score_Real": round(z_score, 2),
                "Preço A": round(p1, 2),
                "Preço B": round(p2, 2),
                "Operação": f"COMPRA {qtd_a} {t1} / VENDA {qtd_b} {t2}" if z_score < 0 else f"VENDA {qtd_a} {t1} / COMPRA {qtd_b} {t2}"
            })
        except:
            continue
    return dados_finais

if st.button('🔍 Escanear Mercado (Dados de Sábado)'):
    resultados = calcular_analise()
    
    # 2. ORDENAÇÃO: Do maior Z-Score absoluto para o menor
    # Isso coloca as maiores oportunidades no topo
    df_exibicao = pd.DataFrame(resultados).sort_values(by="Z_Score_Abs", ascending=False)
    
    for _, row in df_exibicao.iterrows():
        # Define a cor baseada na força do sinal
        cor_header = "gray"
        if row['Z_Score_Abs'] > 2.0:
            cor_header = "green" if row['Z_Score_Real'] < -2.0 else "red"
            
        with st.expander(f"Par: {row['Par']} | Z-Score: {row['Z_Score_Real']}"):
            if row['Z_Score_Abs'] > 2.0:
                st.subheader(f"🚀 Oportunidade Identificada!")
                st.write(f"**Ação Recomendada:** {row['Operação']}")
            else:
                st.write("Distorção pequena. Sugestão: Aguardar.")

st.sidebar.header("Manual de Instruções")
st.sidebar.write("""
1. O Z-Score acima de 2.0 ou abaixo de -2.0 indica distorção estatística.
2. A lista está ordenada pela **maior probabilidade de retorno à média**.
3. Opere no fracionário para manter o risco controlado em R$ 1.000,00.
""")
