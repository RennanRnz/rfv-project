# Imports
import pandas as pd
import streamlit as st
from io import BytesIO

# =========================
# Funções auxiliares
# =========================

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')


@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='RFV')
    writer.close()
    return output.getvalue()


# =========================
# Funções de classificação RFV
# =========================

def recencia_class(x, r, q_dict):
    """
    Quanto menor a recência, melhor o cliente
    """
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'


def freq_val_class(x, fv, q_dict):
    """
    Quanto maior a frequência ou valor, melhor o cliente
    """
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'


# =========================
# Função principal
# =========================

def main():

    st.set_page_config(
        page_title='Segmentação RFV',
        layout='wide',
        initial_sidebar_state='expanded'
    )

    st.title("📊 Segmentação de Clientes RFV")

    st.markdown("""
    RFV significa **Recência, Frequência e Valor** e é uma técnica utilizada para segmentação de clientes
    baseada no comportamento de compras.

    **Componentes:**
    - **Recência (R):** Dias desde a última compra  
    - **Frequência (F):** Número de compras no período  
    - **Valor (V):** Total gasto no período  
    """)

    st.markdown("---")

    # =========================
    # Upload do arquivo
    # =========================

    st.sidebar.header("📁 Upload do arquivo")
    data_file = st.sidebar.file_uploader(
        "Envie um arquivo CSV ou Excel",
        type=['csv', 'xlsx']
    )

    if data_file is None:
        st.info("👈 Faça upload de um arquivo para iniciar a análise.")
        return

    # =========================
    # Leitura do arquivo
    # =========================

    if data_file.name.endswith('.csv'):
        df_compras = pd.read_csv(
            data_file,
            parse_dates=['DiaCompra']
        )
    else:
        df_compras = pd.read_excel(
            data_file,
            parse_dates=['DiaCompra']
        )

    st.subheader("📄 Prévia dos dados")
    st.write(df_compras.head())

    # =========================
    # Recência
    # =========================

    st.subheader("🕒 Recência (R)")

    dia_atual = df_compras['DiaCompra'].max()
    st.write("Data mais recente na base:", dia_atual)

    df_recencia = (
        df_compras
        .groupby('ID_cliente', as_index=False)['DiaCompra']
        .max()
    )

    df_recencia.columns = ['ID_cliente', 'DiaUltimaCompra']
    df_recencia['Recencia'] = (
        df_recencia['DiaUltimaCompra']
        .apply(lambda x: (dia_atual - x).days)
    )

    df_recencia.drop(columns='DiaUltimaCompra', inplace=True)

    st.write(df_recencia.head())

    # =========================
    # Frequência
    # =========================

    st.subheader("🔁 Frequência (F)")

    df_frequencia = (
        df_compras[['ID_cliente', 'CodigoCompra']]
        .groupby('ID_cliente')
        .count()
        .reset_index()
    )

    df_frequencia.columns = ['ID_cliente', 'Frequencia']
    st.write(df_frequencia.head())

    # =========================
    # Valor
    # =========================

    st.subheader("💰 Valor (V)")

    df_valor = (
        df_compras[['ID_cliente', 'ValorTotal']]
        .groupby('ID_cliente')
        .sum()
        .reset_index()
    )

    df_valor.columns = ['ID_cliente', 'Valor']
    st.write(df_valor.head())

    # =========================
    # Tabela RFV
    # =========================

    st.subheader("📌 Tabela RFV")

    df_RFV = (
        df_recencia
        .merge(df_frequencia, on='ID_cliente')
        .merge(df_valor, on='ID_cliente')
    )

    df_RFV.set_index('ID_cliente', inplace=True)
    st.write(df_RFV.head())

    # =========================
    # Segmentação RFV
    # =========================

    st.subheader("🧠 Segmentação RFV")

    quartis = df_RFV.quantile(q=[0.25, 0.50, 0.75])
    st.write("Quartis:")
    st.write(quartis)

    df_RFV['R_quartil'] = df_RFV['Recencia'].apply(
        recencia_class, args=('Recencia', quartis)
    )
    df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(
        freq_val_class, args=('Frequencia', quartis)
    )
    df_RFV['V_quartil'] = df_RFV['Valor'].apply(
        freq_val_class, args=('Valor', quartis)
    )

    df_RFV['RFV_Score'] = (
        df_RFV['R_quartil'] +
        df_RFV['F_quartil'] +
        df_RFV['V_quartil']
    )

    st.write(df_RFV.head())

    # =========================
    # Distribuição dos grupos
    # =========================

    st.subheader("📊 Distribuição dos segmentos")
    st.write(df_RFV['RFV_Score'].value_counts())

    # =========================
    # Ações de Marketing
    # =========================

    st.subheader("🎯 Ações de Marketing / CRM")

    dict_acoes = {
        'AAA': 'Clientes VIP: recompensas, lançamentos exclusivos e programas de fidelidade',
        'DDD': 'Clientes inativos: não priorizar ações',
        'DAA': 'Clientes em risco: campanhas de reativação com descontos',
        'CAA': 'Clientes em risco: campanhas de reativação'
    }

    df_RFV['Ação_Marketing'] = df_RFV['RFV_Score'].map(dict_acoes)

    st.write(df_RFV.head())

    # =========================
    # Download
    # =========================

    st.subheader("⬇️ Download dos resultados")

    df_xlsx = to_excel(df_RFV)

    st.download_button(
        label='📥 Baixar RFV em Excel',
        data=df_xlsx,
        file_name='RFV_resultado.xlsx'
    )

    st.write("Quantidade de clientes por tipo de ação:")
    st.write(df_RFV['Ação_Marketing'].value_counts(dropna=False))


# =========================
# Execução
# =========================

if __name__ == '__main__':
    main()
