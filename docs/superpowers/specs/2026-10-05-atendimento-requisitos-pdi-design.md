
# Atendimento dos requisitos de processamento de imagens

## Objetivo

Adequar o projeto de processamento digital de imagens às exigências fornecidas,
preservando a interface web e a arquitetura atual baseada em Python, OpenCV,
WebSocket e `index.html`.

## Diagnóstico atual

Já existem interface interativa, upload de imagem, captura de câmera, conversões
para cinza e negativo, limiarização manual e por Otsu, filtros de média e
mediana, Canny, erosão, dilatação, abertura, fechamento, histograma e rastreador
KCF.

As lacunas ou problemas identificados são:

1. A contagem de objetos usa uma busca em largura própria, mas a saída é
   parcialmente anotada e não apresenta uma estrutura clara de componentes.
2. Área, perímetro e diâmetro são calculados por componente, porém precisam ser
   unificados para garantir que cada objeto receba sua própria medida.
3. O ramo de processamento de vídeo contém uma condição repetida para imagem,
   impedindo o uso correto de `processVideo`.
4. Não foi localizada reprodução de música quando um objeto é detectado no
   vídeo.
5. Os nomes internos misturam português, inglês, abreviações e grafias
   inconsistentes, como `neighboorMean`, `objects` e `trackVideo`.
6. Há exceções amplas e silenciosas no processamento de imagem e vídeo, que
   escondem falhas reais.

### Funcionalidades que podem ser apresentadas como bônus

Os itens abaixo não são exigidos explicitamente pela rubrica, mas já aparecem
no projeto ou serão preservados como diferenciais. Eles deverão receber
comentários no código identificando-os como bônus:

- `limiarizacao`: permite escolher manualmente o limiar, além do Otsu exigido.
- `normalizacao`: normaliza a faixa de intensidades da imagem.
- `calcular_histograma`: oferece opções cumulativa e normalizada.
- `suavizacao_media` e `suavizacao_mediana`: possuem implementação manual
  para imagens, em vez de depender apenas das funções prontas do OpenCV.
- `rastrear_objeto`: usa o rastreador KCF, enquanto a exigência permite
  qualquer algoritmo de rastreamento.
- As versões de filtros e métricas aplicáveis a vídeo permitem operar sobre
  quadros da câmera em tempo real, além do mínimo necessário para imagens.

## Desenho técnico

### Padronização de nomes

As funções serão renomeadas para português em `snake_case`, de acordo com as
exigências. Exemplos:

- `escala_cinza`
- `negativo`
- `limiarizacao`
- `limiarizacao_otsu`
- `suavizacao_media`
- `suavizacao_mediana`
- `detectar_bordas_canny`
- `erosao`
- `dilatacao`
- `abertura`
- `fechamento`
- `calcular_histograma`
- `rotular_componentes_conexos`
- `calcular_area`
- `calcular_perimetro`
- `calcular_diametro`
- `rastrear_objeto`

Os mapas de funções em `main.py` e as chamadas de vídeo serão atualizados
junto com os nomes, sem aliases duplicados desnecessários.

Comentários curtos `# BÔNUS:` serão colocados somente nas funções acima, sem
adicionar comentários redundantes às funções obrigatórias.

### Processamento de imagens

O upload continuará sendo recebido pelo WebSocket. A cadeia de filtros será
aplicada na ordem selecionada pela interface. A rotulação usará componentes
conexos para identificar objetos distintos e produzir uma imagem anotada. As
medidas serão associadas aos mesmos componentes identificados, evitando que a
área, o perímetro ou o diâmetro de um objeto seja confundido com o de outro.

### Processamento de vídeo

O fluxo de câmera continuará enviando quadros ao servidor. A seleção entre
imagem e vídeo será corrigida para que cada tipo use seu pipeline correto.
O rastreador KCF será mantido como algoritmo de rastreamento. A caixa inicial
continuará sendo criada no centro do primeiro quadro, pois não há atualmente
um seletor manual na interface.

### Reprodução de música

Será incluída uma rotina de alerta de áudio acionada quando o rastreador
retornar uma detecção válida. O alerta terá estado para tocar apenas uma vez
por evento de entrada do objeto, evitando reiniciar a música em todos os
quadros. O caminho do áudio será configurável por constante ou arquivo local.
Se o arquivo não existir ou a biblioteca de áudio não estiver disponível, o
erro será reportado explicitamente e o vídeo continuará funcionando.

### Tratamento de erros

Os blocos `except` genéricos serão substituídos por validações e tratamento
específico dos erros esperados. Imagens inválidas, parâmetros ausentes e falhas
de inicialização do rastreador deverão gerar mensagens claras no servidor ou
na interface, sem retornar uma imagem com aparência de sucesso.

## Validação

1. Verificar a compilação sintática e a importação dos módulos.
2. Executar as funções de conversão e filtros em uma imagem sintética.
3. Validar dois ou mais objetos separados, conferindo contagem, rotulação,
   área, perímetro e diâmetro por objeto.
4. Confirmar que os mapas de imagem e vídeo apontam para as funções renomeadas.
5. Exercitar o caminho de vídeo e confirmar que o rastreador não impede o
   processamento dos quadros.
6. Verificar o comportamento do alerta de áudio com arquivo existente e
   inexistente.

## Escopo excluído

Não será feita uma troca de framework, uma refatoração completa em múltiplos
módulos ou uma alteração visual ampla da interface. Essas mudanças não são
necessárias para atender à rubrica.
