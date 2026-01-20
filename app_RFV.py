# =========================
# Imports
# =========================
import pandas as pd
import streamlit as st
import numpy as np

from datetime import datetime
from io import BytesIO

# =========================
# Configurações iniciais
# =========================
st.set_page_config(
    page_title="RFV - Segmentação de Clientes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Funções utilitárias
# =========================
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


@st.cache_data
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="RFV")
    return output.getvalue()


# =========================
# Funções de classificação RFV
# =========================
def recencia_class(x, r, q_dict):
    """Quanto menor a recência, melhor"""
    if x <= q_dict[r][0.25]:
        return "A"
    elif x <= q_dict[r][0.50]:
        return "B"
    elif x <= q_dict[r][0.75]:
        return "C"
    else:
        return "D"


def freq_val_class(x, fv, q_dict):
    """Quanto maior a frequência/valor, melhor"""
    if x <= q_dict[fv][0.25]:
        return "D"
    elif x <= q_dict[fv][0.50]:
        return "C"
    elif x <= q_dict[fv][0.75]:
        return "B"
    else:
        return "A"


# =========================
# Aplicação principal
# =========================
def main():

    st.title("📊 Segmentação de Clientes com RFV")

    st.markdown(
        """
        RFV significa **Recência, Frequência e Valor** e é uma técnica usada para
        segmentar clientes com base no comportamento de compra.

        **Componentes:**
        - **Recência (R):** Dias desde a última compra  
        - **Frequência (F):** Número de compras no período  
        - **Valor (V):** Total gasto no período  

        O objetivo é apoiar **ações de marketing e CRM mais eficientes**.
        """
    )

    st.markdown("---")

    # =========================
    # Upload do arquivo
    # =========================
    st.sidebar.header("📂 Upload do arquivo")
    uploaded_file = st.sidebar.file_uploader(
        "Envie um arquivo CSV ou Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file is None:
        st.info("👈 Faça o upload de um arquivo para iniciar a análise.")
        return

    # =========================
    # Leitura do arquivo
    # =========================
    try:
        if uploaded_file.name.endswith(".csv"):
            df_compras = pd.read_csv(
                uploaded_file,
                parse_dates=["DiaCompra"],
                infer_datetime_format=True
            )
        else:
            df_compras = pd.read_excel(
                uploaded_file,
                parse_dates=["DiaCompra"]
            )
    except Exception as e:
        st.error(f"❌ Erro ao ler o arquivo: {e}")
        st.stop()

    # =========================
    # Validação das colunas
    # =========================
    colunas_esperadas = {
        "ID_cliente",
        "DiaCompra",
        "CodigoCompra",
        "ValorTotal"
    }

    colunas_arquivo = set(df_compras.columns)

    if not colunas_esperadas.issubset(colunas_arquivo):
        st.error(
            f"""
            ❌ **Arquivo inválido**

            O arquivo deve conter as seguintes colunas obrigatórias:

            `{colunas_esperadas}`

            **Colunas encontradas no arquivo:**
            `{colunas_arquivo}`
            """
        )
        st.stop()

    # =========================
    # Recência
    # =========================
    st.header("🔁 Recência (R)")

    dia_atual = df_compras["DiaCompra"].max()
    st.write(f"📅 Data mais recente na base: **{dia_atual.date()}**")

    df_recencia = (
        df_compras.groupby("ID_cliente", as_index=False)["DiaCompra"]
        .max()
        .rename(columns={"DiaCompra": "DiaUltimaCompra"})
    )

    df_recencia["Recencia"] = (
        df_recencia["DiaUltimaCompra"].apply(lambda x: (dia_atual - x).days)
    )

    df_recencia.drop(columns="DiaUltimaCompra", inplace=True)
    st.dataframe(df_recencia.head())

    # =========================
    # Frequência
    # =========================
    st.header("🔂 Frequência (F)")

    df_frequencia = (
        df_compras.groupby("ID_cliente")["CodigoCompra"]
        .count()
        .reset_index()
        .rename(columns={"CodigoCompra": "Frequencia"})
    )

    st.dataframe(df_frequencia.head())

    # =========================
    # Valor
    # =========================
    st.header("💰 Valor (V)")

    df_valor = (
        df_compras.groupby("ID_cliente")["ValorTotal"]
        .sum()
        .reset_index()
        .rename(columns={"ValorTotal": "Valor"})
    )

    st.dataframe(df_valor.head())

    # =========================
    # Tabela RFV
    # =========================
    st.header("📋 Tabela RFV Final")

    df_RFV = (
        df_recencia
        .merge(df_frequencia, on="ID_cliente")
        .merge(df_valor, on="ID_cliente")
        .set_index("ID_cliente")
    )

    st.dataframe(df_RFV.head())

    # =========================
    # Segmentação
    # =========================
    st.header("🏷 Segmentação RFV")

    quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])
    st.write("📐 Quartis:")
    st.dataframe(quartis)

    df_RFV["R_quartil"] = df_RFV["Recencia"].apply(
        recencia_class, args=("Recencia", quartis)
    )
    df_RFV["F_quartil"] = df_RFV["Frequencia"].apply(
        freq_val_class, args=("Frequencia", quartis)
    )
    df_RFV["V_quartil"] = df_RFV["Valor"].apply(
        freq_val_class, args=("Valor", quartis)
    )

    df_RFV["RFV_Score"] = (
        df_RFV["R_quartil"]
        + df_RFV["F_quartil"]
        + df_RFV["V_quartil"]
    )

    st.dataframe(df_RFV.head())

    # =========================
    # Gráficos
    # =========================
    st.header("📊 Distribuição dos RFV Scores")

    rfv_dist = df_RFV["RFV_Score"].value_counts().sort_index()
    st.bar_chart(rfv_dist)

    # =========================
    # Ações de Marketing
    # =========================
    st.header("🎯 Ações de Marketing / CRM")

    dict_acoes = {
        "AAA": "Clientes VIP – benefícios exclusivos",
        "DDD": "Clientes inativos – sem ação",
        "DAA": "Clientes valiosos em risco – campanha de recuperação",
        "CAA": "Clientes valiosos em risco – campanha de recuperação",
    }

    df_RFV["Ação de Marketing"] = df_RFV["RFV_Score"].map(dict_acoes)

    st.dataframe(df_RFV.head())

    st.subheader("Distribuição das ações")
    acoes_dist = df_RFV["Ação de Marketing"].value_counts(dropna=False)
    st.bar_chart(acoes_dist)

    # =========================
    # Download
    # =========================
    st.header("📥 Download dos Resultados")

    df_xlsx = to_excel(df_RFV.reset_index())
    st.download_button(
        label="⬇️ Baixar RFV em Excel",
        data=df_xlsx,
        file_name="RFV_resultado.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================
# Execução
# =========================
if __name__ == "__main__":
    main()
