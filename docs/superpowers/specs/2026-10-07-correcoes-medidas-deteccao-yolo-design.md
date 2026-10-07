# Correcoes de medidas e deteccao de objetos

## Objetivo

Corrigir o travamento do backend ao executar area, perimetro e diametro e
implementar deteccao e contagem de objetos nos frames de video usando YOLO.
Para imagens binarias, a contagem continuara baseada em componentes conectados.

## Comportamento esperado

- Area, perimetro e diametro processam cada componente da imagem sem filas que
  crescem indefinidamente e sem comparacoes quadraticas desnecessarias.
- Cada componente recebe uma medida propria e e desenhado na imagem retornada.
- A contagem em imagem binaria identifica regioes foreground separadas.
- O filtro de rastreamento de video executa YOLO no frame atual, retornando
  classe, confianca, caixa delimitadora e quantidade total de deteccoes.
- Um frame sem deteccoes retorna lista vazia e nao interrompe o servidor.
- IDs estaveis continuam sendo atribuidos por proximidade para indicar objetos
  novos entre frames.
- O modelo padrao sera carregado sob demanda. Classes dependem do modelo
  escolhido, sem prometer classes que nao existam no conjunto de treinamento.
- Falhas de carregamento ou inferencia do modelo devem gerar erro explicito,
  sem travar silenciosamente o processamento de imagem.

## Desenho tecnico

### Medidas geometricas

Criar uma rotina compartilhada para normalizar uma imagem binaria, obter
componentes conectados e produzir contornos. As operacoes de area, perimetro,
diametro e contagem consumirao o mesmo conjunto de componentes para que todas
as anotacoes se refiram aos mesmos objetos.

- Area: area do contorno ou quantidade de pixels, conforme a convencao atual,
  mantendo `pixelSize` como fator de escala.
- Perimetro: `cv2.arcLength` do contorno externo de cada componente.
- Diametro: diametro do menor circulo envolvente de cada componente, evitando o
  produto cartesiano entre todos os pixels de borda.
- Imagens vazias, dimensoes invalidas e parametros nao positivos serao tratados
  com validacoes claras.

### Deteccao YOLO

Adicionar um adaptador pequeno para o detector, com carregamento lazy do modelo
e configuracao por constante ou variavel de ambiente. O adaptador convertera a
saida do modelo para um formato interno estavel:

```text
{
  id, classe, confianca, bbox, centro
}
```

O resultado anotado exibira caixa, nome da classe, confianca e contagem total.
O detector recebera o frame colorido original; a contagem de componentes
binarios continuara disponivel para o filtro de imagem estatica.

### Fluxo WebSocket

O protocolo binario de PNG sera preservado. Quando o filtro de rastreamento
estiver ativo, o servidor enviara uma mensagem JSON com as deteccoes atuais.
O navegador continuara comparando IDs para reproduzir o alerta apenas quando
um objeto novo aparecer. A lista de IDs sera zerada quando o frame nao tiver
objetos ou quando a fonte mudar.

## Testes

- Testar dois componentes sinteticos e confirmar contagem e anotacao.
- Testar area, perimetro e diametro em componentes pequenos sem travamento.
- Testar imagem vazia e parametros invalidos.
- Testar adaptacao de uma resposta YOLO simulada, incluindo classe, confianca,
  caixa e contagem.
- Testar frame sem deteccoes e falha controlada do detector.
- Executar os testes existentes, compilacao Python e um teste de processamento
  de video com deteccoes simuladas.

## Fora de escopo

- Treinar um modelo customizado.
- Garantir classes que nao estejam no modelo YOLO utilizado.
- Alterar o layout da interface ou o protocolo numerico dos filtros.