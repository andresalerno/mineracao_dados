import pymysql
import pandas as pd

from Orange.data.pandas_compat import table_from_frame


# -----------------------------------------------------
# CONFIGURAÇÃO DO BANCO
# -----------------------------------------------------

HOST = "127.0.0.1"
PORT = 3307
USER = "appuser"
PASSWORD = "Senha AppForte123"
DATABASE = "appdb"


# -----------------------------------------------------
# CONEXÃO
# -----------------------------------------------------

connection = pymysql.connect(
    host=HOST,
    port=PORT,
    user=USER,
    password=PASSWORD,
    database=DATABASE
)


# -----------------------------------------------------
# CONSULTA
# -----------------------------------------------------

query = """
SELECT *
FROM cadastro-clientes;
"""


df = pd.read_sql(query, connection)


# -----------------------------------------------------
# FECHAR CONEXÃO
# -----------------------------------------------------

connection.close()


# -----------------------------------------------------
# CONVERTER PANDAS -> ORANGE
# -----------------------------------------------------

out_data = table_from_frame(df)