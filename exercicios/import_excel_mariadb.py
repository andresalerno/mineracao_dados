#!/usr/bin/env python3
"""Importa abas especificas de um arquivo Excel para tabelas no MariaDB."""

from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


SHEET_TO_TABLE = {
    "cadastro-clientes": "cadastro_clientes",
    "cadastro-produtos": "cadastro_produtos",
    "historico-compras": "historico_compras",
}


def normalize_column_name(name: str) -> str:
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^a-z0-9]+", "_", ascii_name.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "coluna"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Importa 3 abas do Excel para 3 tabelas no MariaDB."
    )
    parser.add_argument(
        "--file",
        default="/home/salerno/workspace/exercicios/base-datos-clientes.xlsx",
        help="Caminho do arquivo Excel.",
    )
    parser.add_argument(
        "--database",
        default="appdb",
        help="Banco de dados de destino.",
    )
    parser.add_argument(
        "--if-exists",
        choices=["fail", "replace", "append"],
        default="replace",
        help="Comportamento quando a tabela ja existe.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host do MariaDB.")
    parser.add_argument("--port", type=int, default=3306, help="Porta do MariaDB.")
    parser.add_argument("--user", default="appuser", help="Usuario do banco.")
    parser.add_argument(
        "--password",
        default="SenhaAppForte123",
        help="Senha do usuario do banco.",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=1000,
        help="Quantidade de linhas por lote na escrita.",
    )
    parser.add_argument(
        "--header",
        type=int,
        default=0,
        help="Indice da linha de cabecalho do Excel (padrao: 0).",
    )
    parser.add_argument(
        "--skip-unnamed",
        action="store_true",
        help="Ignora colunas com nome unnamed_...",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    excel_path = Path(args.file).expanduser().resolve()
    if not excel_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {excel_path}")

    workbook = pd.ExcelFile(excel_path)
    missing = [name for name in SHEET_TO_TABLE if name not in workbook.sheet_names]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Abas obrigatorias nao encontradas: {missing_text}")

    connection_url = (
        f"mysql+pymysql://{args.user}:{args.password}@{args.host}:{args.port}/{args.database}"
    )
    engine = create_engine(connection_url)

    print("Importacao iniciada.")
    print(f"Arquivo: {excel_path}")
    print(f"Banco: {args.database}")

    for sheet_name, table_name in SHEET_TO_TABLE.items():
        df = pd.read_excel(excel_path, sheet_name=sheet_name, header=args.header)

        # Normaliza colunas para nomes SQL previsiveis.
        df.columns = [normalize_column_name(str(col)) for col in df.columns]
        if args.skip_unnamed:
            df = df[[col for col in df.columns if not col.startswith("unnamed")]]

        df.to_sql(
            table_name,
            con=engine,
            if_exists=args.if_exists,
            index=False,
            chunksize=args.chunksize,
            method="multi",
        )

        print(f"Aba '{sheet_name}' -> tabela '{table_name}' ({len(df)} linhas)")
        print(f"Colunas: {', '.join(df.columns)}")

    print("Importacao concluida.")


if __name__ == "__main__":
    main()
