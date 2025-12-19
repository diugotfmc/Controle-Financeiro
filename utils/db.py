import sqlite3
import pandas as pd
import os

# Caminho do banco (compatível com Streamlit Cloud)
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "finance.db")


def get_connection():
    """
    Cria e retorna a conexão com o banco SQLite.
    Garante que a pasta /data exista.
    """
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    return sqlite3.connect(DB_PATH, check_same_thread=False)


def create_table():
    """
    Cria a tabela de gastos caso ainda não exista.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            forma_pagamento TEXT NOT NULL,
            tipo TEXT NOT NULL,
            parcela_atual INTEGER,
            total_parcelas INTEGER
        )
    """)

    conn.commit()
    conn.close()


def insert_gastos(df: pd.DataFrame):
    """
    Insere um DataFrame de gastos no banco.
    Espera as colunas no padrão do modelo.
    """
    if df.empty:
        return

    conn = get_connection()
    df.to_sql(
        "gastos",
        conn,
        if_exists="append",
        index=False
    )
    conn.close()


def load_gastos() -> pd.DataFrame:
    """
    Carrega todos os gastos do banco.
    """
    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM gastos",
        conn,
        parse_dates=["data"]
    )

    conn.close()
    return df


def delete_gasto(gasto_id: int):
    """
    Remove um gasto específico pelo ID.
    (Útil para correções futuras)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM gastos WHERE id = ?",
        (gasto_id,)
    )

    conn.commit()
    conn.close()
