# E-commerce Purchase Propensity

Pipeline de treinamento para estimar a probabilidade de compra a partir de
um recorte de navegação de uma sessão de e-commerce. O modelo inicial é uma
regressão logística, comparada a um baseline que prevê a taxa de compra do treino.

## Estado atual
Implementados: contrato de CSV, validação, preparação, treino, métricas,
registro no MLflow, DAG DVC, imagem de treino e CI.
O repositório não inclui dados de clientes nem resultados de negócio validados.
O gerador sintético serve para testar a execução. A seleção da fonte real,
validação temporal e definição do limiar operacional estão pendentes.

## Ambiente
Python 3.11 ou 3.12. A CI e a imagem Docker utilizam Python 3.11.
```sh
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
python -m pytest -q
```

## Executar com dados de sessões
Disponibilize `data/raw/sessions.csv` conforme [o contrato de dados](docs/data-contract.md).
```sh
python scripts/run.py
mlflow ui --backend-store-uri ./mlruns --host 127.0.0.1
```
Saídas: `models/purchase_propensity.joblib`, `reports/metrics.json` e `mlruns/`.
O modelo serializado contém o pré-processamento e oferece `predict_proba`.
Carregue somente artefatos de origem confiável.

Para uma execução local sem dados reais, gere uma entrada sintética:
```sh
python scripts/create_demo_data.py data/raw/sessions.csv
python scripts/run.py
```
O gerador recusa sobrescrever um arquivo existente. Métricas sintéticas não
demonstram capacidade de prever compras reais.

## Versionamento com DVC
Na primeira utilização em um clone Git:
```sh
dvc init
dvc repro
git add .dvc .dvcignore dvc.yaml dvc.lock params.yaml .gitignore
git commit -m "Track training pipeline with DVC"
```
`dvc.lock` é gerado com os hashes da execução e deve acompanhar o código.
Os arquivos em `data/raw` são dependências externas: para compartilhá-los,
execute `dvc add data/raw/sessions.csv` e versione o arquivo `.dvc` resultante.
Configure um remoto antes de usar `dvc push` e `dvc pull` entre máquinas.
Credenciais devem ficar na configuração local ou em variáveis de ambiente.
O diretório MLflow local não é sincronizado pelo DVC.

## Containers
```sh
docker build -t ecommerce-purchase-propensity:local .
docker run --rm -v "<CAMINHO_ABSOLUTO_DOS_DADOS>:/app/data/raw:ro" ecommerce-purchase-propensity:local
```
A pasta montada deve conter `sessions.csv` e permitir leitura pelo usuário do container.
As saídas permanecem no container; para preservá-las, configure volumes graváveis
ou tracking remoto. O manifesto em `infra/kubernetes/train-job.yaml` é um ponto
de partida: exige uma imagem acessível ao cluster e um PVC existente chamado
`purchase-propensity-data`, contendo o CSV. Não houve implantação em cluster.

## Validação automática
O workflow executa testes de contrato e treinamento, reproduz o DAG DVC e
constrói e executa a imagem com dados sintéticos. Não faz deploy nem publica imagem.

## Próximas decisões
Consulte [a arquitetura](docs/architecture.md), [o contrato](docs/data-contract.md)
e [o roadmap](docs/roadmap.md) para limites, critérios e próximos passos.
