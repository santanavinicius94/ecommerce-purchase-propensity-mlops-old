# Roadmap

1. Selecionar uma fonte de sessões com licença e documentação de coleta.
2. Confirmar o instante de decisão, janela de compra e disponibilidade das features.
3. Criar a ingestão da fonte real e validar o contrato, evitando vazamento do alvo.
4. Adicionar separação temporal e controle de clientes entre conjuntos.
5. Comparar regressão logística, baseline e modelos candidatos com validação.
6. Definir métrica de negócio, orçamento de campanha e limiar operacional.
7. Registrar o dataset com DVC, gerar dvc.lock e configurar armazenamento remoto.
8. Fixar dependências transitivas e imagem base; reproduzir em um clone limpo.
9. Configurar MLflow compartilhado, persistência de artefatos e execução em cluster.

## Critérios para a primeira avaliação real
- Fonte e licença registradas; alvo e janela documentados.
- Features disponíveis no instante da decisão.
- Separação de treino, validação e teste sem sobreposição indevida.
- Baseline e modelo avaliados no mesmo conjunto, com métricas rastreáveis.
- Conjunto de teste preservado durante a escolha de modelo e limiar.
- Execução reproduzível e limitações relatadas junto aos resultados.
