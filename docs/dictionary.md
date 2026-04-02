# 📖 Dicionário de Código — AI Talent Gap in Alberta

---

## Sprint 1 — Data Ingestion

| Termo | Tipo | Explicação |
|---|---|---|
| `RAW_DATA_PATH` | variável (string) | Caminho absoluto para a pasta onde ficam os arquivos brutos originais. Nunca modificamos arquivos nessa pasta. |
| `PROCESSED_DATA_PATH` | variável (string) | Caminho para a pasta onde salvamos os dados após limpeza e transformação. |
| `RAW_FILES` | variável (dict) | Dicionário que mapeia um nome interno padronizado para o nome real do arquivo. Facilita referências no código sem depender do nome original do arquivo. |
| `standardize_columns()` | função | Recebe um DataFrame e retorna o mesmo com nomes de colunas em minúsculas, sem espaços e sem caracteres especiais. Evita erros de referência por capitalização. |
| `validate_dataframe()` | função | Imprime um relatório de qualidade de um DataFrame: número de linhas/colunas, valores nulos por coluna e tipos de dados. Usada para detectar problemas antes de transformar os dados. |
| `load_csv()` | função | Carrega um arquivo CSV tentando múltiplos encodings (utf-8, latin-1, cp1252). Retorna um DataFrame padronizado ou vazio em caso de erro. |
| `load_excel()` | função | Carrega todas as abas de um arquivo Excel. Retorna um dicionário onde cada chave é o nome da aba e o valor é o DataFrame correspondente. |
| `run_ingestion()` | função | Função principal que orquestra o carregamento de todos os datasets. Retorna um dicionário com todos os DataFrames prontos para uso. |
| `encoding` | conceito | Define como os caracteres de texto são representados em bytes. UTF-8 é o padrão moderno; latin-1 e cp1252 são comuns em dados mais antigos ou canadenses. |
| `DataFrame` | conceito (pandas) | Estrutura de dados tabular do pandas, similar a uma planilha Excel. Tem linhas e colunas nomeadas. É o objeto central de toda análise de dados em Python. |
| `sheet_name=None` | parâmetro (pandas) | Quando passado para `pd.read_excel()`, instrui o pandas a carregar TODAS as abas do arquivo, retornando um dicionário em vez de um único DataFrame. |
| `df.isnull().sum()` | expressão (pandas) | Conta quantos valores nulos (NaN) existem em cada coluna de um DataFrame. Essencial para avaliar qualidade dos dados. |
| `os.path.abspath(__file__)` | expressão (Python) | Retorna o caminho absoluto do arquivo Python que está sendo executado. Usado para construir caminhos relativos de forma robusta. |

---

## Sprint 2 — Data Cleaning & Transformation

| Termo | Tipo | Explicação |
|---|---|---|
| `parse_wages()` | função | Recebe uma string no formato `'$29.09 / $53.11 / $80.91'` e retorna uma tupla com os 3 valores como float. Usa `re.findall` para extrair números decimais. |
| `map_outlook_score()` | função | Converte o texto do outlook (ex: `'Above Average'`) para um número de 1 a 3. Permite ordenar e comparar ocupações quantitativamente. |
| `OUTLOOK_SCORE_MAP` | variável (dict) | Dicionário que mapeia cada valor textual de outlook para um score numérico. 3 = alta demanda, 2 = média, 1 = baixa. |
| `parse_occupation_blocks()` | função | Percorre o Excel linha a linha detectando blocos de ocupação (NOC code + 4 métricas). Transforma a estrutura visual do Excel em dados estruturados. |
| `pivot_to_wide()` | função | Converte formato longo (uma linha por ocupação/ano/métrica) para formato largo (uma linha por ocupação/ano, colunas = métricas). Usa `pd.pivot_table`. |
| `demand_supply_ratio` | feature (coluna) | Razão entre `net_change_job_openings` e `net_change_job_seekers`. Valores > 1.0 indicam mais vagas que candidatos — sinal de talent gap. |
| `gap_flag` | feature (coluna) | Variável binária (0 ou 1). Vale 1 quando há mais vagas abertas do que candidatos disponíveis naquele ano. |
| `is_ai_related` | feature (coluna) | Flag binária no dataset de graduados. Vale 1 se o campo de estudo contém palavras-chave relacionadas a IA/tech. |
| `income_avg_5yr` | feature (coluna) | Média da renda do graduado ao longo dos 5 anos após formatura. Proxy de estabilidade e trajetória salarial. |
| `inc_growth` | coluna (graduate_outcomes) | Crescimento percentual de renda entre y1 e y5. Convertido de string `'24%'` para float `0.24`. |
| `low_memory=False` | parâmetro (pandas) | Instrui o pandas a ler o CSV inteiro antes de inferir tipos. Evita o `DtypeWarning` quando uma coluna tem tipos mistos (ex: `naics` com int e string). |
| `header=None` | parâmetro (pandas) | Diz ao pandas para não usar nenhuma linha como cabeçalho. Essencial quando o arquivo tem estrutura não-padrão, como o Excel do Occupational Outlook. |
| `zfill(5)` | método (Python/pandas) | Preenche uma string com zeros à esquerda até atingir o tamanho especificado. Ex: `'211'.zfill(5)` → `'00211'`. Usado para padronizar códigos NOC. |
| `NOC code` | conceito | National Occupational Classification — código de 5 dígitos usado no Canadá para identificar cada ocupação de forma única. Ex: `21231` = Software Engineers. |

---

## Sprint 3 — Data Modeling & Pipeline

| Termo | Tipo | Explicação |
|---|---|---|
| `star schema` | conceito | Modelo de dados dimensional com uma tabela fato central conectada a múltiplas tabelas dimensão. Otimizado para queries analíticas. |
| `dim_occupation` | tabela (dimensão) | Tabela mestre de ocupações com 513 registros. Combina dados de AI Profiles + Occupational Outlook. Contém NOC code, nome, salários, outlook score. |
| `dim_time` | tabela (dimensão) | Tabela temporal com 11 anos (2023-2033). Inclui year_offset e period_label para facilitar análises temporais. |
| `dim_municipality` | tabela (dimensão) | Tabela de municípios de Alberta (420 registros). Inclui total de empresas e taxa de participação no mercado de trabalho. |
| `fact_talent_gap` | tabela (fato) | Tabela central do modelo com 5.643 registros (513 ocupações × 11 anos). Contém métricas de gap e o AI Talent Gap Index. |
| `supply_analysis` | tabela (analítica) | Tabela complementar com 184 programas de graduação. Analisa o supply de talentos por campo de estudo com score de atratividade. |
| `AI Talent Gap Index` | métrica (calculada) | Score de 0-100 que combina demand/supply ratio (50%), cumulative imbalance (30%) e outlook score (20%). Indica severidade do gap. |
| `gap_category` | coluna (classificação) | Categoriza o gap em Low (0-30), Moderate (31-60) ou Critical (61-100). Facilita filtros e visualizações. |
| `is_ai_adjacent` | flag (coluna) | Vale 1 se a ocupação está no dataset de AI Profiles (12 ocupações tech). Vale 0 para as demais 501 ocupações. |
| `attractiveness_score` | métrica (supply) | Score de 0-100 que combina renda média (50%), crescimento de renda (30%) e volume de graduados (20%). Indica atratividade do campo de estudo. |
| `demand_supply_ratio` | métrica (fato) | Razão entre vagas abertas e candidatos disponíveis. > 1.0 = mais vagas que candidatos (gap). < 1.0 = excesso de oferta. |
| `cumulative_imbalance` | métrica (fato) | Acúmulo do gap ao longo do tempo. Valores positivos indicam déficit crescente de talentos. |
| `years_with_gap` | métrica (agregada) | Quantos anos (de 0 a 11) a ocupação teve gap_flag = 1. Indica persistência do gap ao longo da década. |
| `pivot_table()` | função (pandas) | Transforma dados de formato longo para largo. Usado para converter métricas em colunas separadas. |
| `groupby().agg()` | expressão (pandas) | Agrupa dados por uma ou mais colunas e aplica funções de agregação (mean, sum, count). Essencial para criar métricas resumidas. |
| `merge()` | função (pandas) | Faz join entre dois DataFrames. Similar ao JOIN do SQL. Usado para conectar dimensões com fatos. |
| `apply()` | método (pandas) | Aplica uma função a cada linha ou coluna de um DataFrame. Usado para calcular o Talent Gap Index linha a linha. |


---

## Conceitos Gerais de Engenharia de Dados

| Termo | Tipo | Explicação |
|---|---|---|
| `ETL` | conceito | Extract, Transform, Load — processo de extrair dados de fontes, transformá-los e carregá-los em um destino. Nosso pipeline segue esse padrão. |
| `Pipeline` | conceito | Sequência automatizada de etapas de processamento de dados. Nosso pipeline: raw → processed → analytics → insights. |
| `Data Lineage` | conceito | Rastreamento da origem e transformações dos dados. Cada tabela analytics tem lineage clara até os arquivos raw. |
| `Idempotência` | conceito | Propriedade de um processo que pode ser executado múltiplas vezes sem efeitos colaterais. Nossos scripts são idempotentes — rodar 2x produz o mesmo resultado. |
| `Integridade Referencial` | conceito | Garantia de que chaves estrangeiras apontam para registros existentes. Validamos que todos os NOCs do fact existem em dim_occupation. |
| `Granularidade` | conceito | Nível de detalhe dos dados. Nossa tabela fato tem granularidade ocupação/ano (5.643 registros = 513 ocupações × 11 anos). |
| `Cardinalidade` | conceito | Número de valores únicos em uma coluna. Ex: noc_code tem cardinalidade 513 na dim_occupation. |
| `Surrogate Key` | conceito | Chave primária artificial (ex: occupation_id, time_id). Usada em vez de chaves naturais (noc_code, year) para simplificar joins. |
| `Slowly Changing Dimension` | conceito | Dimensão que muda ao longo do tempo. Não aplicamos SCD neste projeto (dados são snapshot de 2024), mas seria necessário em produção. |

---

## Sprint 4 — API REST + Segurança

| Termo | Tipo | Explicação |
|---|---|---|
| `FastAPI` | framework | Framework Python moderno para APIs REST. Gera documentação Swagger automaticamente a partir dos type hints. |
| `Pydantic` | biblioteca | Valida e serializa dados usando type hints Python. Se um campo vier com tipo errado, retorna erro 422 automaticamente. |
| `APIRouter` | classe (FastAPI) | Agrupa endpoints relacionados. Similar a um Blueprint do Flask. Permite organizar a API em módulos separados. |
| `Depends()` | função (FastAPI) | Sistema de injeção de dependências. Permite compartilhar funções (ex: carregar dados) entre múltiplos endpoints sem repetição. |
| `@lru_cache` | decorator (Python) | Memoriza o resultado de uma função. Usado em `load_datasets()` para carregar os CSVs apenas uma vez, não a cada request. |
| `response_model` | parâmetro (FastAPI) | Define o schema Pydantic que valida e documenta a resposta do endpoint. FastAPI rejeita respostas que não conformam ao schema. |
| `Query()` | função (FastAPI) | Define parâmetros de query string com validação. Ex: `year: int = Query(ge=2023, le=2033)` rejeita anos fora do range. |
| `HTTPException` | classe (FastAPI) | Lança erros HTTP padronizados. `raise HTTPException(404)` retorna `{"detail": "..."}` com status 404. |
| `CORS` | conceito (segurança) | Cross-Origin Resource Sharing. Controla quais domínios podem fazer requests à API. Configurado via `CORSMiddleware`. |
| `Rate Limiting` | conceito (segurança) | Limita o número de requests por IP por período. Protege contra abuso e DDoS. Implementado com `slowapi`. |
| `Security Headers` | conceito (OWASP) | Headers HTTP que protegem contra ataques comuns: `X-Frame-Options` (clickjacking), `X-Content-Type-Options` (sniffing), `HSTS` (força HTTPS). |
| `OWASP` | conceito | Open Web Application Security Project. Lista as principais vulnerabilidades e boas práticas de segurança para APIs web. |
| `Health Check` | endpoint | Endpoint `/health` que verifica se a API está funcionando. Usado por sistemas de monitoramento e load balancers. |
| `Paginação` | conceito | Divide grandes resultados em páginas. Evita retornar 169k registros de uma vez. Parâmetros: `page` e `page_size`. |
| `TestClient` | classe (Starlette) | Permite testar endpoints FastAPI sem subir um servidor real. Faz requests HTTP diretamente na aplicação ASGI. |
| `NaN` | conceito (pandas) | Not a Number — valor nulo em colunas numéricas do pandas. JSON não aceita NaN, precisa ser convertido para `null` (None). |
| `Entry point` | conceito | Arquivo principal que inicia uma aplicação. `main.py` é o entry point da API; `run_full_pipeline.py` é o entry point do pipeline. |
| `Middleware` | conceito | Código que executa em todas as requests antes/depois dos endpoints. Usado para adicionar headers de segurança, logging, etc. |
| `Dependency Injection` | padrão | Padrão onde dependências são "injetadas" nas funções em vez de criadas dentro delas. Facilita testes e reutilização. |
