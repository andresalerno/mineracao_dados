# Claude AI Customization for Data Mining Repository

This is an educational repository for data mining and data analysis using Python and related tools.

## Project Overview

- **Purpose**: Teaching data mining, analysis, and visualization techniques
- **Target Audience**: Students learning data analysis workflows
- **Primary Language**: Python 3.12
- **Documentation Language**: Portuguese (Brazil)

## Environment & Setup

### Conda Environment
- **Environment Name**: `datamining`
- **Location**: `/home/salerno/miniforge3/envs/datamining`
- **Configuration**: [`conda-envs/datamining/environment.yml`](conda-envs/datamining/environment.yml)
- **Key Libraries**: JupyterLab, Pandas, NumPy, Scikit-learn, SciPy, Matplotlib, Seaborn, Plotly, DuckDB, Polars

To activate the environment:
```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate datamining
```

### Docker Services
- **MariaDB Database**: Defined in [`exercicios/docker-compose.yml`](exercicios/docker-compose.yml)
  - Host: `127.0.0.1`, Port: `3307`
  - Database: `appdb`
  - User: `appuser` / Password: `SenhaAppForte123`
  - Root Password: `SenhaRootForte123`
  - Character Set: UTF-8 MB4 (important for international characters)

Start services: `cd exercicios && docker-compose up -d`

## Project Structure

```
workspace/
├── README.md                          # Main setup guide for the environment
├── aulas/                             # Lessons (Orange Data Mining workflows)
│   └── aula_*.ows, aula_*.md         # Orange workflows & notes
├── exercicios/                        # Exercises
│   ├── docker-compose.yml             # Database configuration
│   ├── import_excel_mariadb.py        # Script to load Excel → MariaDB
│   ├── conexao_mariadb.py             # Example database connection
│   ├── lista_01/                      # Exercise set 1
│   │   ├── exercicio_03/              # Exploratory analysis (Orange)
│   │   ├── exercicio_04/
│   │   ├── exercicio_05/
│   │   └── exercicio_06/              # Database persistence & SQL
│   └── data/ & various Excel/CSV files
└── datasets/                          # Reference datasets (e.g., netflix_titles.csv)
```

Each exercise typically contains:
- `README.md` — Exercise description and solution steps
- `data/` — Input files (Excel, CSV)
- `project/` — Orange Data Mining workflow files (`.ows`)
- `img/` — Screenshots and visualizations

## Key Conventions

### 1. **Documentation Format**
- Markdown with embedded images and math notation (KaTeX)
- Portuguese language (typical style: formal, educational tone)
- Examples: Math as inline $\mu$ or block equations with `$$`
- File links use standard Markdown syntax

### 2. **Data Handling**
- **Primary Sources**: Excel files (`.xlsx`) and CSV files
- **Processing Tool**: Pandas for tabular data, Polars for performance
- **Database Work**: MariaDB (note: MySQL/MariaDB compatibility)
- **Common Pattern**: Read from Excel → Process → Store in MariaDB
- **Script Reference**: [`import_excel_mariadb.py`](exercicios/import_excel_mariadb.py) is the main ETL utility

### 3. **Orange Data Mining**
- Visual tool for exploratory analysis and visualization
- Workflow files saved as `.ows` (Orange Workflow Saved)
- Common widgets: CSV Import, Data Table, Distributions, Scatter Plot, Rank
- When helping with Orange workflows: describe widget sequences clearly
- Workflows are stored per exercise in `project/` folders

### 4. **Python Scripts**
- Entry point pattern: `source ~/miniforge3/etc/profile.d/conda.sh && conda activate datamining && python script.py`
- Database connections: Use `pymysql` library (see [`conexao_mariadb.py`](exercicios/lista_01/conexao_mariadb.py))
- Parameterized scripts: Use argparse for CLI arguments
- Common CLI pattern: `--file`, `--host`, `--port`, `--database`, `--user`, `--if-exists`

### 5. **Exercise Solutions**
- **Format**: README.md with questions (a, b, c, d...) and illustrated answers
- **Visualizations**: Include screenshots of Orange workflows and analysis outputs
- **Statistics**: Report means (μ), standard deviations (σ), correlations (r) with proper notation
- **Key Insights**: Answer shows both numerical results and interpretation

### 6. **Special Considerations**
- **Timezone**: America/Sao_Paulo (configured in docker-compose)
- **Encoding**: Always UTF-8 MB4 for database character sets (Portuguese accents)
- **Error Handling**: Many exercises involve database operations—handle connection errors gracefully
- **Data Validation**: Exercises often require checking record counts after operations

## Common Tasks

### Running Excel → MariaDB Import
```bash
cd exercicios/lista_01/exercicio_06
python ../../../import_excel_mariadb.py \
    --file data/exercicio_6.xlsx \
    --host 127.0.0.1 \
    --port 3307 \
    --database appdb \
    --user appuser \
    --if-exists replace \
    --skip-unnamed
```

### Connecting to MariaDB Manually
```bash
docker exec mariadb mariadb -uappuser -pSenhaAppForte123 appdb -e "SHOW TABLES;"
```

### Running Python with Conda
```bash
source ~/miniforge3/etc/profile.d/conda.sh
conda activate datamining
python script.py
```

## When Helping with This Codebase

1. **Exercise Support**: When editing/creating exercises, follow the structure: README.md with numbered questions, data/ folder, and project/ folder for Orange workflows
2. **Documentation**: Use proper Portuguese terminology and maintain the educational tone
3. **Database Work**: Always verify docker-compose is running and credentials match
4. **Analysis Code**: Prefer Pandas for data manipulation, Plotly/Matplotlib for visualization
5. **Math Notation**: Use KaTeX inline ($...$) and block ($$...$$) syntax as shown in existing exercises
6. **Testing**: Test scripts in the conda environment; don't assume system Python

## Related Documentation
- Main setup guide: [README.md](README.md)
- Docker configuration: [exercicios/docker-compose.yml](exercicios/docker-compose.yml)
- Environment definition: [conda-envs/datamining/environment.yml](conda-envs/datamining/environment.yml)
