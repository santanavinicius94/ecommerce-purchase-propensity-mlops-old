# Arquitetura

CSV de sessões → validação → CSV preparado → split estratificado →
pré-processamento ajustado no treino → regressão logística → modelo e métricas.

O ColumnTransformer padroniza as variáveis numéricas e aplica one-hot encoding
às categóricas. O pré-processamento faz parte do Pipeline serializado e é
ajustado apenas no conjunto de treino. session_id e purchased não são features.

## Experimentos e avaliação
O MLflow registra parâmetros, hash SHA-256 do CSV, tamanho dos conjuntos,
métricas e artefatos. MLFLOW_TRACKING_URI permite selecionar um servidor externo;
sem essa variável, usa-se o diretório local mlruns.

Average precision é a métrica inicial para avaliar ordenação de propensão em
classes potencialmente desbalanceadas. ROC AUC e Brier score complementam a
avaliação. Precision, recall, F1 e accuracy usam o limiar configurável de 0,5.
O baseline usa a prevalência no treino e é avaliado no mesmo holdout.
Não há meta numérica de negócio definida; custos de contato, capacidade da
campanha e conversão devem orientar a escolha do limiar, usando validação.

## Reprodutibilidade e limites
DVC descreve as dependências do pipeline; Git mantém código e configuração.
As dependências diretas são fixadas, mas ainda falta um lock completo de
transitivas e a fixação da imagem base por digest.

Docker executa treino em lote. O Job Kubernetes é um exemplo de configuração
com entrada em PVC; persistência de saídas, registry e tracking compartilhado
precisam ser configurados antes de uma execução operacional.
Não há API, serving, monitoramento online ou implantação automática.
O split atual é uma verificação inicial de treinamento, sujeito às limitações
de independência e temporalidade descritas no contrato de dados.
