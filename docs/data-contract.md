# Contrato de dados

Entrada: CSV UTF-8, separado por vírgulas, uma linha por sessão.

| Campo | Tipo | Regra |
|---|---|---|
| session_id | identificador | único e não vazio; excluído do modelo |
| pages_viewed | inteiro | contagem não negativa no instante do recorte |
| time_on_site_seconds | número | tempo acumulado não negativo no recorte |
| cart_items | inteiro | itens no carrinho no recorte; não negativo |
| traffic_source | texto | origem do tráfego; não vazio |
| device_type | texto | tipo de dispositivo; não vazio |
| purchased | inteiro 0 ou 1 | compra após o recorte, dentro da janela de observação |

Não são aceitos valores ausentes ou numéricos infinitos. O treino exige as duas
classes, com pelo menos 10 exemplos de cada. Colunas adicionais são descartadas
antes do treino. Categorias desconhecidas no uso do modelo são aceitas pelo encoder.

## Semântica a validar na fonte real
O ponto de partida proposto é um recorte aos cinco minutos da sessão e uma
janela de compra nas 24 horas seguintes. Esses parâmetros ainda precisam ser
confirmados com a fonte dos dados e não são verificáveis pelo CSV atual.
Sessões com compra anterior ao recorte devem ser excluídas; o alvo deve ser
calculado apenas após a janela completa, sem usar informação futura nas features.
Se a fonte não permitir essa reconstrução, redefina o contrato antes do treino.

O split aleatório atual pressupõe sessões independentes. Ele não evita o mesmo
cliente em treino e teste nem simula mudança temporal. Antes de avaliar dados reais,
adicione timestamps e identificador anonimizado de cliente para split temporal
e controle de sobreposição. Não inclua nomes, e-mails ou dados de pagamento no CSV.
