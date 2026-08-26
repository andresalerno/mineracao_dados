 # Exercício 06 — Persistência e investigação no MariaDB

Este exercício utiliza o arquivo [`data/exercicio_6.xlsx`](data/exercicio_6.xlsx), que possui as abas:

- `cadastro-clientes`
- `cadastro-produtos`
- `historico-compras`

## 1. Persistir os dados no MariaDB

O container `mariadb` já está configurado pelo arquivo [`docker-compose.yml`](../../../docker-compose.yml), com o banco `appdb` disponível na porta `3307` do Ubuntu/WSL.

Com o ambiente `datamining` ativo, execute a partir desta pasta:

```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate datamining
python ../../../import_excel_mariadb.py \
	--file data/exercicio_6.xlsx \
	--host 127.0.0.1 \
	--port 3307 \
	--database appdb \
	--user appuser \
	--if-exists replace \
	--skip-unnamed
```

O parâmetro `--if-exists replace` substitui o conteúdo das três tabelas sem alterar o container, o banco, as credenciais ou o volume persistente. O script cria as seguintes tabelas:

| Aba do Excel | Tabela no MariaDB | Registros |
|---|---|---:|
| `cadastro-clientes` | `cadastro_clientes` | 30 |
| `cadastro-produtos` | `cadastro_produtos` | 50 |
| `historico-compras` | `historico_compras` | 100 |

Para conferir a carga:

```bash
docker exec mariadb mariadb -uappuser -pSenhaAppForte123 appdb -e \
	"SHOW TABLES; SELECT 'cadastro_clientes' AS tabela, COUNT(*) AS registros FROM cadastro_clientes UNION ALL SELECT 'cadastro_produtos', COUNT(*) FROM cadastro_produtos UNION ALL SELECT 'historico_compras', COUNT(*) FROM historico_compras;"
```

## 2. Conectar o Orange ao banco

1. Abra o Orange Data Mining.
2. Instale/abra o add-on de conexão SQL, caso o widget `SQL Table` não esteja disponível.
3. No canvas, adicione o widget `SQL Table`.
4. Crie uma conexão MySQL/MariaDB com estes parâmetros:

| Parâmetro | Valor |
|---|---|
| Host | `127.0.0.1` |
| Porta | `3307` |
| Banco de dados | `appdb` |
| Usuário | `appuser` |
| Senha | `SenhaAppForte123` |

5. Selecione uma das tabelas `cadastro_clientes`, `cadastro_produtos` ou `historico_compras`.
6. Conecte `SQL Table` aos widgets `Data Table` e `Feature Statistics` para visualizar e investigar os dados.

## 3. Conectar via Python (Pandas + SQLAlchemy) e enviar para o Orange

Além da conexão direta pelo widget `SQL Table`, é possível ler os dados do container `mariadb` em Python usando `pandas` e `sqlalchemy`, e depois converter o `DataFrame` para uma tabela do Orange com `Orange.data.pandas_compat`.

Essa abordagem é útil dentro de widgets do tipo `Python Script` no Orange, ou em notebooks/scripts que fazem parte de um pipeline maior antes da análise visual.

```python
import pandas as pd
from sqlalchemy import create_engine
from Orange.data.pandas_compat import table_from_frame

# Dados de conexão
host = "127.0.0.1"
port = 3307
user = "appuser"
password = "SenhaAppForte123"
database = "appdb"

# Cria conexão
connection_url = (
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
)

engine = create_engine(connection_url)

# Consulta
query = """
SELECT *
FROM cadastro_clientes;
"""

# MariaDB -> Pandas
df = pd.read_sql(query, engine)

print(df.head())
print(f"Registros encontrados: {len(df)}")

# Pandas -> Orange
out_data = table_from_frame(df)

engine.dispose()
```

Pontos importantes:

- A string de conexão usa o driver `pymysql` (`mysql+pymysql://...`), que é compatível com MariaDB.
- Host (`127.0.0.1`), porta (`3307`), usuário (`appuser`), senha (`SenhaAppForte123`) e banco (`appdb`) são os mesmos parâmetros usados na conexão do Orange, definidos em [`docker-compose.yml`](../../../docker-compose.yml).
- `pd.read_sql` executa a query e devolve um `DataFrame` do Pandas com o resultado.
- `table_from_frame(df)` converte o `DataFrame` em uma `Orange.data.Table`, permitindo usar o resultado em widgets do Orange conectados na saída do `Python Script`.
- `engine.dispose()` encerra a conexão com o banco ao final da execução.
- Basta trocar o nome da tabela na cláusula `FROM` da `query` para consultar `cadastro_produtos` ou `historico_compras`.

## 4. Investigação

### a) Quais problemas foram encontrados?

Nesta base, **não foram encontrados problemas de qualidade** nas verificações realizadas. As três tabelas foram lidas corretamente e apresentaram:

- nenhum valor vazio;
- nenhuma linha completamente duplicada;
- nenhum identificador repetido nas tabelas de cadastro ou no histórico;
- nenhum `ID do Cliente` ou `ID do Produto` sem correspondência;
- nenhuma quantidade ou valor total menor ou igual a zero;
- nenhum total de compra diferente do cálculo `quantidade × preço de venda`.

### b) Em quais campos eles apareceram?

Como não foram encontrados problemas, **nenhum campo foi afetado**. Foram analisados, principalmente:

- identificação: `ID Cliente`, `ID Produto` e `ID da Compra`;
- cadastro: `Nome Cliente`, `CPF`, `Estado`, `CEP`, `Preço de Custo` e `Preço de Venda`;
- compras: `ID do Cliente`, `ID do Produto`, `Qtde de Produtos Comprados` e `Valor Total Pago`.

### c) Quantos registros foram afetados?

**0 registros** foram afetados pelos problemas investigados. A carga contém 180 registros no total: 30 clientes, 50 produtos e 100 compras.

### d) O fato de os dados estarem armazenados em um banco de dados garante que eles estejam corretos?

Não. O banco de dados garante principalmente que os dados sejam **armazenados, organizados e consultados** de forma estruturada. Ele pode aplicar regras técnicas, como tipos de dados, chaves primárias, campos obrigatórios e relacionamentos, mas isso não garante que a informação represente a realidade.

Por exemplo, um estado escrito com uma sigla existente pode ser aceito pelo banco, mesmo que esteja associado ao cliente errado. Da mesma forma, uma data pode ter formato válido, mas representar uma data incorreta. Por isso, a qualidade depende também de validações de domínio, comparação com fontes confiáveis, regras de negócio e análise no Orange.

Neste exercício, os testes realizados não apontaram erros na base, mas essa conclusão se limita às regras e verificações aplicadas.
