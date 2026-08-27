# Exercício 02 — Gestão Acadêmica

**Ferramentas:** Excel, MariaDB (Docker) e Power BI

## Enunciado

Criar quatro tabelas pequenas relacionadas por identificadores:

| Tabela | Volume aproximado | Identificador |
|---|---:|---|
| Alunos | ~30 alunos | ID do aluno |
| Cursos | ~4 cursos | ID do curso |
| Disciplinas | ~12 disciplinas | ID da disciplina |
| Matrículas | ~100 registros | ID da matrícula |

Primeiro montar tudo corretamente no Excel. Depois: importar o arquivo para o Power BI, criar os relacionamentos entre as tabelas, mostrar a **quantidade de alunos por curso** e a **quantidade de matrículas por disciplina** e responder:

- **a)** Qual curso possui mais alunos?
- **b)** Qual disciplina possui mais matrículas?
- **c)** Por que utilizar várias tabelas relacionadas pode ser melhor do que colocar todas as informações em uma única tabela?

## 1. Base de dados

A base é o arquivo [`data/exercicio_02.xlsx`](data/exercicio_02.xlsx). Ele contém **5 abas**, mas apenas quatro são dados oficiais do exercício:

| Aba | Registros | Papel no modelo | Colunas |
|---|---:|---|---|
| `Alunos` | 30 | dimensão de estudantes | `ID_Aluno`, `Nome_Aluno`, `Data_Nascimento`, `Genero`, `Email`, `ID_Curso`, `Data_Ingresso`, `Status_Aluno` |
| `Cursos` | 4 | dimensão de cursos | `ID_Curso`, `Nome_Curso`, `Area_Conhecimento`, `Duracao_Semestres`, `Modalidade`, `Coordenador` |
| `Disciplinas` | 12 | dimensão de disciplinas | `ID_Disciplina`, `ID_Curso`, `Nome_Disciplina`, `Carga_Horaria`, `Semestre_Recomendado`, `Tipo` |
| `Matriculas` | 100 | tabela fato (eventos) | `ID_Matricula`, `ID_Aluno`, `ID_Disciplina`, `Data_Matricula`, `Periodo`, `Nota_1`, `Nota_2`, `Nota_Final`, `Frequencia`, `Situacao` |
| ~~`Power BI`~~ | — | guia de análise (texto de apoio) | **não é dado — deve ser ignorada na importação** |

> A aba `Power BI` é apenas um roteiro em texto (relacionamentos, medidas DAX e respostas esperadas). **A aba oficial de eventos é `Matriculas`** — se houver qualquer outra aba parecida no arquivo, ela deve ser descartada e `Matriculas` considerada como a verdadeira.

### 1.1 Observação sobre as chaves

O arquivo tem **inconsistência de formato nos identificadores** entre as abas — algo comum quando as tabelas são digitadas separadamente no Excel:

| Relação | Chave no lado 1 | Chave no lado * | Formatos batem? | Tratamento |
|---|---|---|:--:|---|
| Cursos → Alunos | `Cursos.ID_Curso` = `1..4` (número) | `Alunos.ID_Curso` = `1..4` (número) | ✅ | — |
| Disciplinas → Matrículas | `Disciplinas.ID_Disciplina` = `1..12` (número) | `Matriculas.ID_Disciplina` = `1..12` (número) | ✅ | — |
| Cursos → Disciplinas | `Cursos.ID_Curso` = `1..4` (número) | `Disciplinas.ID_Curso` = `C001..C004` (texto) | ❌ | corrigido na carga — [seção 2.3](#23-correção-do-id_curso-em-academico_disciplinas) |
| Alunos → Matrículas | `Alunos.ID_Aluno` = `1..30` (número) | `Matriculas.ID_Aluno` = `A001..A030` (texto) | ❌ | corrigido na carga — [seção 2.4](#24-correção-do-id_aluno-em-academico_matriculas) |

Depois desses dois ajustes, as quatro chaves são inteiras e os relacionamentos fecham diretamente, sem nenhum registro órfão.

## 2. Importação das abas para o container MariaDB

### 2.1 Pré-requisitos

O container `mariadb` é o definido em [`exercicios/docker-compose.yml`](../../docker-compose.yml) (imagem `mariadb:11.4`, banco `appdb`, porta **`3307`** no host, usuário `appuser`).

```bash
# subir o banco, se ainda não estiver rodando
cd /home/salerno/workspace/exercicios
docker compose up -d
docker exec mariadb mariadb-admin ping -uappuser -pSenhaAppForte123   # -> "mysqld is alive"

# ambiente Python com pandas + sqlalchemy + pymysql
source ~/miniforge3/etc/profile.d/conda.sh
conda activate datamining
```

### 2.2 Carga das 4 abas

Usa-se o utilitário do repositório [`import_excel_mariadb.py`](../../import_excel_mariadb.py). Ele **já contém o mapeamento de Gestão Acadêmica** e importa exatamente as quatro abas oficiais, ignorando a aba `Power BI` automaticamente:

```python
GESTAO_ACADEMICA_SHEET_TO_TABLE = {
    "Alunos":      "academico_alunos",
    "Cursos":      "academico_cursos",
    "Disciplinas": "academico_disciplinas",
    "Matriculas":  "academico_matriculas",
}
```

Para cada aba o script lê o cabeçalho, normaliza os nomes das colunas para `snake_case` sem acento (`ID_Aluno` → `id_aluno`, `Nota_Final` → `nota_final`) e grava a tabela com `if_exists="replace"` (apaga e recria com o conteúdo novo).

```bash
cd /home/salerno/workspace/exercicios/lista_01/exercicio_02

python ../../import_excel_mariadb.py \
    --file data/exercicio_02.xlsx \
    --host 127.0.0.1 \
    --port 3307 \
    --database appdb \
    --user appuser \
    --if-exists replace \
    --skip-unnamed
```

Saída esperada:

```
Aba 'Alunos'      -> tabela 'academico_alunos'       (30 linhas)
Aba 'Cursos'      -> tabela 'academico_cursos'       (4 linhas)
Aba 'Disciplinas' -> tabela 'academico_disciplinas' (12 linhas)
Aba 'Matriculas'  -> tabela 'academico_matriculas'  (100 linhas)
Importacao concluida.
```

Resultado no banco:

| Aba do Excel | Tabela no MariaDB | Registros |
|---|---|---:|
| `Alunos` | `academico_alunos` | 30 |
| `Cursos` | `academico_cursos` | 4 |
| `Disciplinas` | `academico_disciplinas` | 12 |
| `Matriculas` | `academico_matriculas` | 100 |

> **Backup antes de sobrescrever** (opcional, recomendado se as tabelas já existirem):
> ```bash
> for t in academico_alunos academico_cursos academico_disciplinas academico_matriculas; do
>   docker exec mariadb mariadb-dump -uappuser -pSenhaAppForte123 appdb "$t" > "${t}_backup.sql"
> done
> ```

### 2.3 Correção do `id_curso` em `academico_disciplinas`

Na aba `Disciplinas` do Excel a coluna `ID_Curso` está com o **código errado** (`C001..C004`, em texto), enquanto `Cursos.ID_Curso` é o inteiro `1..4`. A tabela `academico_disciplinas` é regravada convertendo `C00n` → `n`, para que a chave estrangeira aponte de fato para `academico_cursos`:

```python
import re, unicodedata
import pandas as pd
from sqlalchemy import create_engine

def norm(name):
    a = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii")
    n = re.sub(r"[^a-z0-9]+", "_", a.strip().lower())
    return re.sub(r"_+", "_", n).strip("_") or "coluna"

f = "data/exercicio_02.xlsx"
df = pd.read_excel(f, sheet_name="Disciplinas", header=0)
df.columns = [norm(c) for c in df.columns]
df = df[[c for c in df.columns if not c.startswith("unnamed")]]

# 'C001' -> 1, alinhando com academico_cursos.id_curso (inteiro 1..4)
df["id_curso"] = df["id_curso"].astype(str).str.extract(r"(\d+)").astype(int)

eng = create_engine("mysql+pymysql://appuser:SenhaAppForte123@127.0.0.1:3307/appdb")
df.to_sql("academico_disciplinas", con=eng, if_exists="replace", index=False,
          chunksize=1000, method="multi")
```

Depois da regravação, `academico_disciplinas.id_curso` é `bigint` com valores `1..4` e o join com `academico_cursos` é direto:

| id_disciplina | id_curso | nome_curso | nome_disciplina |
|---:|---:|---|---|
| 1–3 | 1 | Administração | Fundamentos de Administração, Contabilidade Geral, Marketing |
| 4–6 | 2 | Sistemas de Informação | Lógica de Programação, Banco de Dados, Engenharia de Software |
| 7–9 | 3 | Pedagogia | Didática, Psicologia da Educação, Políticas Educacionais |
| 10–12 | 4 | Engenharia de Produção | Cálculo Aplicado, Gestão da Produção, Pesquisa Operacional |

> Alternativa sem Python: `UPDATE academico_disciplinas SET id_curso = CAST(REGEXP_REPLACE(id_curso, '[^0-9]', '') AS UNSIGNED);` — funciona, mas mantém a coluna como `text`; a regravação acima já a deixa numérica.

### 2.4 Correção do `id_aluno` em `academico_matriculas`

Na aba `Matriculas` a coluna `ID_Aluno` está no **padrão errado** (`A001..A030`, em texto), quando deveria ser o inteiro `1..30` de `Alunos.ID_Aluno`. A tabela `academico_matriculas` é regravada convertendo `A00n` → `n`:

```python
import re, unicodedata
import pandas as pd
from sqlalchemy import create_engine

def norm(name):
    a = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode("ascii")
    n = re.sub(r"[^a-z0-9]+", "_", a.strip().lower())
    return re.sub(r"_+", "_", n).strip("_") or "coluna"

f = "data/exercicio_02.xlsx"
df = pd.read_excel(f, sheet_name="Matriculas", header=0)
df.columns = [norm(c) for c in df.columns]
df = df[[c for c in df.columns if not c.startswith("unnamed")]]

# 'A001' -> 1, alinhando com academico_alunos.id_aluno (inteiro 1..30)
df["id_aluno"] = df["id_aluno"].astype(str).str.extract(r"(\d+)").astype(int)

eng = create_engine("mysql+pymysql://appuser:SenhaAppForte123@127.0.0.1:3307/appdb")
df.to_sql("academico_matriculas", con=eng, if_exists="replace", index=False,
          chunksize=1000, method="multi")
```

Depois da regravação, `academico_matriculas.id_aluno` é `bigint` com valores `1..30` e o join com `academico_alunos` é direto — sem coluna auxiliar.

> Alternativa sem Python: `UPDATE academico_matriculas SET id_aluno = CAST(REGEXP_REPLACE(id_aluno, '[^0-9]', '') AS UNSIGNED);` — funciona, mas mantém a coluna como `text`; a regravação acima já a deixa numérica.

### 2.5 Verificação da carga

```sql
-- contagens
SELECT 'alunos' t, COUNT(*) n FROM academico_alunos
UNION ALL SELECT 'cursos',      COUNT(*) FROM academico_cursos
UNION ALL SELECT 'disciplinas', COUNT(*) FROM academico_disciplinas
UNION ALL SELECT 'matriculas',  COUNT(*) FROM academico_matriculas;

-- integridade referencial (todas devem retornar 0)
SELECT COUNT(*) FROM academico_matriculas   m LEFT JOIN academico_alunos      a ON a.id_aluno     = m.id_aluno       WHERE a.id_aluno     IS NULL;
SELECT COUNT(*) FROM academico_matriculas   m LEFT JOIN academico_disciplinas d ON d.id_disciplina = m.id_disciplina   WHERE d.id_disciplina IS NULL;
SELECT COUNT(*) FROM academico_disciplinas  d LEFT JOIN academico_cursos      c ON c.id_curso     = d.id_curso       WHERE c.id_curso     IS NULL;
SELECT COUNT(*) FROM academico_alunos       a LEFT JOIN academico_cursos      c ON c.id_curso     = a.id_curso       WHERE c.id_curso     IS NULL;
```

| Verificação | Resultado |
|---|---:|
| `academico_alunos` | 30 |
| `academico_cursos` | 4 |
| `academico_disciplinas` | 12 |
| `academico_matriculas` | 100 |
| Matrículas órfãs (aluno / disciplina) | 0 / 0 |
| Disciplinas / alunos sem curso | 0 / 0 |

Rodar tudo de uma vez pelo terminal:

```bash
docker exec -i mariadb mariadb -uappuser -pSenhaAppForte123 appdb < verificacao.sql
```

## 3. Conexão do Power BI com o MariaDB

**Obter Dados → MariaDB**, apontando para o mesmo banco `appdb`:

| Parâmetro | Valor |
|---|---|
| Servidor | `127.0.0.1:3307` (a partir do Windows) ou `localhost:3307` (a partir do WSL) |
| Banco de dados | `appdb` |
| Usuário | `appuser` |
| Senha | `SenhaAppForte123` |
| Modo de conectividade | Import (ou DirectQuery) |

Selecionar as quatro tabelas `academico_alunos`, `academico_cursos`, `academico_disciplinas` e `academico_matriculas`. Se os ajustes das seções [2.3](#23-correção-do-id_curso-em-academico_disciplinas) e [2.4](#24-correção-do-id_aluno-em-academico_matriculas) **não** tiverem sido feitos no banco, replicá-los no Power Query:

- `academico_matriculas`: converter `id_aluno` com `Number.FromText(Text.Select([id_aluno], {"0".."9"}))`
- `academico_disciplinas`: converter `id_curso` com `Number.FromText(Text.Select([id_curso], {"0".."9"}))`

## 4. Modelo de relacionamentos

`academico_matriculas` é a tabela fato; as outras três são dimensões. Todos os relacionamentos são **1:\*** com **filtro cruzado em sentido único** (da dimensão para o fato):

| Lado 1 (dimensão) | Lado \* (filho) | Chave | Cardinalidade |
|---|---|---|:--:|
| `academico_cursos` | `academico_alunos` | `id_curso` → `id_curso` | 1:\* |
| `academico_cursos` | `academico_disciplinas` | `id_curso` → `id_curso` (corrigido na [seção 2.3](#23-correção-do-id_curso-em-academico_disciplinas)) | 1:\* |
| `academico_alunos` | `academico_matriculas` | `id_aluno` → `id_aluno` (corrigido na [seção 2.4](#24-correção-do-id_aluno-em-academico_matriculas)) | 1:\* |
| `academico_disciplinas` | `academico_matriculas` | `id_disciplina` → `id_disciplina` | 1:\* |

Esquema resultante (modelo estrela, com `Cursos` num segundo nível acima de `Alunos` e `Disciplinas`):

```
academico_cursos ──1:*──> academico_alunos ──1:*──> academico_matriculas
        │                                                   ^
        └──────1:*──────> academico_disciplinas ──1:*───────┘
```

Visão de relacionamentos do Power BI, já com as quatro chaves inteiras (seções [2.3](#23-correção-do-id_curso-em-academico_disciplinas) e [2.4](#24-correção-do-id_aluno-em-academico_matriculas)):

![Diagrama de relacionamentos entre as quatro tabelas no Power BI](img/relacionamento.jpg)

> Coloque as demais capturas (visuais, painel) em [`img/`](img/) e o arquivo `.pbix` em [`project/`](project/).

## 5. Medidas DAX e visuais

| Medida | DAX | Visual |
|---|---|---|
| `Qtd Alunos` | `Qtd Alunos = DISTINCTCOUNT(academico_alunos[id_aluno])` | Barras — Eixo: `academico_cursos[nome_curso]`, Valor: `[Qtd Alunos]` |
| `Qtd Matrículas` | `Qtd Matrículas = COUNTROWS(academico_matriculas)` | Barras — Eixo: `academico_disciplinas[nome_disciplina]`, Valor: `[Qtd Matrículas]` |

Validação: sem filtros, os totais devem ser **30 alunos** e **100 matrículas**.

## 6. Respostas

### Quantidade de alunos por curso

| Curso | Alunos | Ativos | Trancados |
|---|---:|---:|---:|
| Administração | **8** | 7 | 1 |
| Sistemas de Informação | **8** | 8 | 0 |
| Pedagogia | 7 | 6 | 1 |
| Engenharia de Produção | 7 | 6 | 1 |
| **Total** | **30** | 27 | 3 |

```sql
SELECT c.nome_curso, COUNT(*) AS qtd_alunos
FROM academico_alunos a
JOIN academico_cursos c ON c.id_curso = a.id_curso
GROUP BY c.nome_curso
ORDER BY qtd_alunos DESC;
```

### Quantidade de matrículas por disciplina

| ID | Disciplina | Curso | Matrículas |
|---:|---|---|---:|
| 1 | Fundamentos de Administração | Administração | **11** |
| 4 | Lógica de Programação | Sistemas de Informação | **11** |
| 7 | Didática | Pedagogia | 9 |
| 10 | Cálculo Aplicado | Engenharia de Produção | 9 |
| 2 | Contabilidade Geral | Administração | 8 |
| 3 | Marketing | Administração | 8 |
| 5 | Banco de Dados | Sistemas de Informação | 8 |
| 6 | Engenharia de Software | Sistemas de Informação | 8 |
| 8 | Psicologia da Educação | Pedagogia | 7 |
| 9 | Políticas Educacionais | Pedagogia | 7 |
| 11 | Gestão da Produção | Engenharia de Produção | 7 |
| 12 | Pesquisa Operacional | Engenharia de Produção | 7 |
| | | **Total** | **100** |

```sql
SELECT d.id_disciplina, d.nome_disciplina, COUNT(*) AS qtd_matriculas
FROM academico_matriculas m
JOIN academico_disciplinas d ON d.id_disciplina = m.id_disciplina
GROUP BY d.id_disciplina, d.nome_disciplina
ORDER BY qtd_matriculas DESC;
```

### a) Qual curso possui mais alunos?

**Empate entre Administração e Sistemas de Informação, com 8 alunos cada** (contra 7 de Pedagogia e 7 de Engenharia de Produção).

Como critério de desempate, considerando apenas alunos com `Status_Aluno = 'Ativo'`, **Sistemas de Informação fica à frente, com 8 alunos ativos** (todos os seus alunos estão ativos), enquanto Administração tem 7 ativos e 1 trancado.

### b) Qual disciplina possui mais matrículas?

**Empate entre `Fundamentos de Administração` (ID 1) e `Lógica de Programação` (ID 4), com 11 matrículas cada.** As duas são disciplinas obrigatórias de 1º semestre dos dois cursos maiores, e cada uma foi cursada por 8 alunos distintos (algumas com repetição em 2025.1 e 2025.2). As seguintes são `Didática` e `Cálculo Aplicado`, com 9 matrículas.

### c) Por que várias tabelas relacionadas em vez de uma única tabela?

- **Menos redundância.** Numa tabela única, o nome do curso, o coordenador, a carga horária da disciplina etc. se repetiriam em cada uma das 100 linhas de matrícula. No modelo relacional cada fato é escrito uma só vez.
- **Consistência (integridade).** Corrigir "Sistemas de Informação" ou trocar o coordenador de um curso é uma única alteração em `Cursos`. Na tabela única haveria dezenas de cópias e o risco de ficarem divergentes ("Sist. Informação", "SI"...).
- **Menos anomalias de inserção/exclusão.** É possível cadastrar um curso ou uma disciplina que ainda não tem matrículas; e apagar a última matrícula de um aluno não apaga o cadastro dele.
- **Chaves garantem validade.** Os relacionamentos por `ID` impedem uma matrícula apontar para um aluno ou disciplina inexistente — as verificações da [seção 2.5](#25-verificação-da-carga) retornaram 0 órfãos.
- **Economia de espaço e desempenho.** Tabelas-dimensão pequenas e uma fato enxuta (só IDs + medidas) ocupam menos e agregam mais rápido.
- **Análises flexíveis.** Com o modelo estrela, o mesmo conjunto de fatos responde "alunos por curso", "matrículas por disciplina", "matrículas por área de conhecimento", "por modalidade (EAD/Presencial)" etc. só arrastando campos das dimensões — sem refazer a base. É exatamente o formato para o qual a engine do Power BI (VertiPaq + DAX) foi otimizada.
