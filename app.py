import streamlit as st
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

from utils.db import (
    create_table,
    insert_gastos,
    load_gastos,
    delete_gasto
)

# ======================
# CONFIGURAÇÕES INICIAIS
# ======================
st.set_page_config(
    page_title="Controle Financeiro",
    layout="wide"
)

create_table()

# ======================
# SIDEBAR
# ======================
st.sidebar.title("💰 Controle Financeiro")
menu = st.sidebar.radio(
    "Menu",
    [
        "Registrar Gasto",
        "Parcelas Existentes",
        "Resumo Mensal",
        "Compromissos Futuros"
    ]
)

CATEGORIAS = [
    "Alimentação", "Moradia", "Transporte",
    "Lazer", "Saúde", "Educação", "Outros"
]

# ======================
# REGISTRAR GASTO
# ======================
if menu == "Registrar Gasto":
    st.title("📝 Registrar Gasto")

    with st.form("form_gasto"):
        col1, col2 = st.columns(2)

        with col1:
            data_compra = st.date_input(
                "Data da compra",
                value=date.today()
            )
            descricao = st.text_input("Descrição")
            categoria = st.selectbox("Categoria", CATEGORIAS)

        with col2:
            valor_total = st.number_input(
                "Valor total (R$)",
                min_value=0.0,
                format="%.2f"
            )
            forma_pagamento = st.selectbox(
                "Forma de pagamento",
                ["Débito", "Pix", "Dinheiro", "Crédito"]
            )
            tipo = st.selectbox("Tipo", ["Fixo", "Variável"])

            parcelas = 1
            if forma_pagamento == "Crédito":
                parcelas = st.number_input(
                    "Número de parcelas",
                    min_value=1,
                    step=1
                )

        submitted = st.form_submit_button("Salvar gasto")

        if submitted:
            if not descricao:
                st.error("Informe uma descrição.")
            elif valor_total <= 0:
                st.error("Valor deve ser maior que zero.")
            else:
                registros = []

                valor_parcela = (
                    valor_total / parcelas
                    if forma_pagamento == "Crédito"
                    else valor_total
                )

                for i in range(parcelas):
                    registros.append({
                        "data": data_compra + relativedelta(months=i),
                        "descricao": descricao,
                        "categoria": categoria,
                        "valor": round(valor_parcela, 2),
                        "forma_pagamento": forma_pagamento,
                        "tipo": tipo,
                        "parcela_atual": i + 1 if forma_pagamento == "Crédito" else None,
                        "total_parcelas": parcelas if forma_pagamento == "Crédito" else None
                    })

                df = pd.DataFrame(registros)
                insert_gastos(df)

                st.success("Gasto registrado com sucesso!")

# ======================
# PARCELAS EXISTENTES
# ======================
elif menu == "Parcelas Existentes":
    st.title("💳 Parcelas já existentes no cartão")

    st.info(
        "Use esta tela para registrar compras feitas no passado "
        "que ainda terão parcelas futuras no cartão."
    )

    with st.form("form_parcelas_existentes"):
        descricao = st.text_input("Descrição da compra")
        categoria = st.selectbox("Categoria", CATEGORIAS)

        valor_total = st.number_input(
            "Valor total da compra (R$)",
            min_value=0.0,
            format="%.2f"
        )

        total_parcelas = st.number_input(
            "Total de parcelas",
            min_value=1,
            step=1
        )

        parcela_atual = st.number_input(
            "Parcela atual",
            min_value=1,
            step=1
        )

        data_proxima_fatura = st.date_input(
            "Data da próxima fatura"
        )

        submitted = st.form_submit_button("Cadastrar parcelas futuras")

        if submitted:
            if parcela_atual > total_parcelas:
                st.error("Parcela atual não pode ser maior que o total.")
            else:
                registros = []
                parcelas_restantes = total_parcelas - parcela_atual + 1
                valor_parcela = valor_total / total_parcelas

                for i in range(parcelas_restantes):
                    registros.append({
                        "data": data_proxima_fatura + relativedelta(months=i),
                        "descricao": descricao,
                        "categoria": categoria,
                        "valor": round(valor_parcela, 2),
                        "forma_pagamento": "Crédito",
                        "tipo": "Variável",
                        "parcela_atual": parcela_atual + i,
                        "total_parcelas": total_parcelas
                    })

                df = pd.DataFrame(registros)
                insert_gastos(df)

                st.success("Parcelas futuras cadastradas com sucesso!")

# ======================
# RESUMO MENSAL
# ======================
elif menu == "Resumo Mensal":
    st.title("📅 Resumo Mensal")

    df = load_gastos()

    if df.empty:
        st.warning("Nenhum gasto registrado.")
    else:
        df["mes"] = df["data"].dt.to_period("M").astype(str)

        mes_selecionado = st.selectbox(
            "Selecione o mês",
            sorted(df["mes"].unique(), reverse=True)
        )

        df_mes = df[df["mes"] == mes_selecionado].sort_values("data")

        total_mes = df_mes["valor"].sum()

        col1, col2 = st.columns(2)
        col1.metric("Total gasto no mês", f"R$ {total_mes:,.2f}")
        col2.metric("Quantidade de lançamentos", len(df_mes))

        st.subheader("📋 Detalhamento")
        st.dataframe(df_mes, use_container_width=True)

        st.subheader("📊 Gastos por categoria")
        gasto_categoria = (
            df_mes.groupby("categoria")["valor"]
            .sum()
            .sort_values(ascending=False)
        )
        st.bar_chart(gasto_categoria)

# ======================
# COMPROMISSOS FUTUROS
# ======================
elif menu == "Compromissos Futuros":
    st.title("📆 Compromissos Financeiros Futuros")

    df = load_gastos()

    if df.empty:
        st.warning("Nenhum gasto registrado.")
    else:
        hoje = pd.to_datetime(date.today())
        futuros = df[df["data"] > hoje]

        if futuros.empty:
            st.info("Nenhum compromisso futuro.")
        else:
            resumo = (
                futuros
                .groupby(futuros["data"].dt.to_period("M"))["valor"]
                .sum()
                .reset_index()
            )

            resumo["data"] = resumo["data"].astype(str)

            st.subheader("📊 Comprometimento mensal futuro")
            st.bar_chart(resumo.set_index("data"))

            st.subheader("📋 Detalhamento")
            st.dataframe(
                futuros.sort_values("data"),
                use_container_width=True
            )
