import streamlit as st
import pandas as pd
import os
from datetime import date

# ======================
# Configurações iniciais
# ======================
st.set_page_config(
    page_title="Controle Financeiro",
    layout="wide"
)

DATA_PATH = "data/gastos.csv"

# ======================
# Funções auxiliares
# ======================
def load_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH, parse_dates=["data"])
    else:
        return pd.DataFrame(columns=[
            "data", "descricao", "categoria",
            "valor", "forma_pagamento", "tipo"
        ])

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

# ======================
# Sidebar
# ======================
st.sidebar.title("📊 Controle Financeiro")
menu = st.sidebar.radio(
    "Menu",
    ["Registrar Gasto", "Resumo Mensal"]
)

# ======================
# Página: Registrar Gasto
# ======================
if menu == "Registrar Gasto":
    st.title("📝 Registrar Gasto")

    with st.form("form_gasto"):
        col1, col2 = st.columns(2)

        with col1:
            data = st.date_input("Data", value=date.today())
            descricao = st.text_input("Descrição")
            categoria = st.selectbox(
                "Categoria",
                [
                    "Alimentação", "Moradia", "Transporte",
                    "Lazer", "Saúde", "Educação", "Outros"
                ]
            )

        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
            forma_pagamento = st.selectbox(
                "Forma de Pagamento",
                ["Crédito", "Débito", "Pix", "Dinheiro"]
            )
            tipo = st.selectbox(
                "Tipo",
                ["Fixo", "Variável"]
            )

        submitted = st.form_submit_button("Salvar")

        if submitted:
            df = load_data()
            novo_registro = pd.DataFrame([{
                "data": data,
                "descricao": descricao,
                "categoria": categoria,
                "valor": valor,
                "forma_pagamento": forma_pagamento,
                "tipo": tipo
            }])

            df = pd.concat([df, novo_registro], ignore_index=True)
            save_data(df)

            st.success("Gasto registrado com sucesso!")

# ======================
# Página: Resumo Mensal
# ======================
elif menu == "Resumo Mensal":
    st.title("📅 Resumo Mensal")

    df = load_data()

    if df.empty:
        st.warning("Nenhum gasto registrado ainda.")
    else:
        df["mes"] = df["data"].dt.to_period("M").astype(str)

        mes_selecionado = st.selectbox(
            "Selecione o mês",
            sorted(df["mes"].unique(), reverse=True)
        )

        df_mes = df[df["mes"] == mes_selecionado]

        total_gasto = df_mes["valor"].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total gasto no mês", f"R$ {total_gasto:,.2f}")
        col2.metric("Quantidade de lançamentos", len(df_mes))

        st.subheader("📋 Gastos detalhados")
        st.dataframe(df_mes.sort_values("data"))

        st.subheader("📊 Gastos por categoria")
        gasto_categoria = (
            df_mes.groupby("categoria")["valor"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(gasto_categoria)
