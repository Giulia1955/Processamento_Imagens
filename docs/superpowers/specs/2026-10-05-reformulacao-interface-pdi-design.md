# Reformulacao da interface de processamento de imagens

## Objetivo

Reformular a tela web do aplicativo de processamento digital de imagens para
melhorar a hierarquia visual, a leitura em notebooks e a usabilidade dos fluxos
de carregar uma imagem, iniciar a camera, aplicar filtros e removê-los.

A direcao visual aprovada e **Estudio editorial tecnico**: uma interface escura,
compacta e autoral, com verde menta como cor de acao e destaque. A reformulacao
preserva o servidor Python, o protocolo WebSocket e a funcionalidade atual dos
filtros.

## Contexto e diagnostico

A interface atual concentra quase toda a tela em um layout fixo de 80% para o
visualizador e 20% para os controles. Os filtros aparecem em uma coluna longa,
com pouco agrupamento e muitos campos ocultos. Os filtros ativos ficam em uma
trilha inferior estreita e a remocao depende de clique do meio ou da tecla Shift,
o que nao e descobrivel para a maioria dos usuarios.

Tambem foram identificados estes problemas:

- nao ha hierarquia clara entre fonte de imagem, visualizador, filtros disponiveis
e filtros ativos;
- os itens ativos nao exibem seus parametros;
- a remocao de um filtro pode depender de indices capturados na criacao do DOM;
- nao existem estados claros para conexao, carregamento, erro e ausencia de imagem;
- o uso de larguras fixas e alturas percentuais pode quebrar em notebooks menores;
- botoes e campos nao possuem uma linguagem visual consistente de hover, foco,
desabilitado e ativo;
- os controles dependem fortemente de `onclick` inline;
- a tela nao oferece feedback suficiente depois do envio de um quadro ou filtro;
- a interface tem baixo suporte explicito a teclado, foco visivel e nomes
acessiveis.

## Usuarios e cenario principal

O usuario trabalha em um notebook durante uma aula ou atividade de laboratorio.
Ele alterna entre uma imagem carregada e a camera, aplica uma sequencia de
operacoes, compara o resultado visual e remove ou edita um filtro no meio da
sequencia. O fluxo deve ser eficiente para uso repetido e nao depender de
comportamentos de mouse pouco comuns.

## Direcao visual

### Paleta

- Fundo principal: grafite quase preto, para manter foco no visualizador.
- Superficies: azul-esverdeado escuro, separando painel, barra e controles.
- Acao primaria: verde menta, usado em botoes principais, filtros ativos,
foco e estados positivos.
- Texto principal: branco suave, evitando branco puro em grandes areas.
- Texto secundario: cinza esverdeado com contraste suficiente.
- Erros: vermelho coral discreto, reservado para mensagens e estados de falha.

A paleta deve evitar uma composicao monocromatica: o verde menta sera uma cor
de acao e nao o fundo dominante de toda a pagina.

### Tipografia e densidade

Usar uma familia tipografica expressiva para titulos e uma familia sans-serif
legivel para controles, sem depender de Arial, Roboto ou Inter como identidade
principal. Os titulos devem ter escala moderada, adequada a uma ferramenta, e
os controles devem priorizar leitura rapida. Os cards e paineis terao cantos
sutis, de no maximo 8px, sem aninhar cards desnecessariamente.

## Estrutura da tela

```text
Cabecalho
  marca/nome da ferramenta
  estado da conexao
  alternancia Camera | Imagem
  acao de carregar imagem

Conteudo principal
  visualizador da imagem
    estado vazio, carregando, erro ou resultado
  painel lateral de filtros
    ajustes basicos
    realce e bordas
    morfologia
    medicao e analise
    rastreamento

Trilha inferior
  titulo "Filtros aplicados"
  itens ativos com nome, parametros e botao X
  estado vazio quando nao houver filtros
```

O visualizador deve ocupar a maior area disponivel e preservar a proporcao da
imagem com `object-fit: contain`. O painel lateral deve ter rolagem propria se
necessario, sem deslocar o visualizador. A trilha inferior deve permanecer
visivel e ter rolagem horizontal quando a cadeia de filtros crescer.

## Interacoes e comportamento

### Fonte de imagem

- `Imagem` abre o seletor de arquivo.
- `Camera` inicia ou encerra a captura, com estado visual explicito.
- A acao indisponivel durante processamento deve ficar desabilitada.
- Ao trocar a fonte, a cadeia de filtros existente deve ser preservada somente
se ainda for compativel; caso contrario, a interface deve informar a limpeza.

### Aplicacao e edicao de filtros

- Filtros sem parametros aplicam imediatamente.
- Filtros parametrizados exibem o campo junto ao respectivo controle.
- O valor deve ser validado antes do envio, com mensagem curta de erro proxima
ao campo.
- Clicar no corpo de um filtro ativo reabre seus parametros para edicao.
- A ordem dos filtros ativos e a ordem enviada ao servidor devem ser identicas.
- A trilha mostra parametros relevantes, por exemplo `Canny · 5 / 50`.

### Remocao por X

Cada filtro ativo sera renderizado como um item horizontal com botao `X`:

```text
[ Grayscale                                      X ]
[ Canny · 5 / 50                                X ]
```

O botao `X` deve:

- ser visualmente identificavel;
- possuir area de toque/click adequada;
- ter `aria-label` como `Remover filtro Canny`;
- mostrar tooltip para mouse;
- nao disparar a abertura do editor do filtro;
- remover somente o item clicado;
- reaplicar automaticamente os filtros restantes;
- restaurar a imagem original quando o ultimo filtro for removido.

A implementacao deve renderizar a trilha a partir do estado atual, em vez de
capturar indices fixos em closures dos elementos. Isso evita que a remocao de
um item do meio aponte para o filtro errado.

### Estados da interface

A tela deve representar explicitamente:

- desconectado: WebSocket indisponivel;
- conectando: conexao em andamento;
- pronto: aguardando uma imagem;
- carregando: arquivo ou quadro sendo enviado;
- processando: filtro sendo aplicado;
- resultado: imagem processada disponivel;
- erro: mensagem acionavel e nao apenas log no console.

O estado vazio deve explicar a proxima acao de forma curta, por exemplo
`Carregue uma imagem ou inicie a camera`.

## Acessibilidade e usabilidade

- Todos os botoes devem ser elementos `button`, nao `div` clicavel.
- Todos os campos devem ter label ou nome acessivel.
- Foco visivel para teclado em botoes, campos e itens ativos.
- Ordem de tabulacao deve seguir cabecalho, fonte, visualizador, painel e
trilha de filtros.
- Contraste de texto e controles deve atender WCAG AA sempre que possivel.
- O `X` deve ser acessivel por teclado e nao depender de clique do meio ou Shift.
- Mensagens de erro e status devem usar uma regiao com `aria-live` quando
forem atualizadas dinamicamente.
- Hover nao pode ser o unico meio de comunicar uma mudanca de estado.

## Responsividade

O alvo principal e desktop/notebook. A largura do painel lateral deve usar
limites flexiveis, mantendo a imagem como prioridade. Em larguras menores:

- o painel pode reduzir sua largura ate um minimo legivel;
- a trilha inferior deve rolar horizontalmente;
- textos e botoes nao podem sobrepor outros elementos;
- controles secundarios podem ser reorganizados em duas colunas;
- nao e necessario criar uma experiencia completa para celular.

## Arquitetura de implementacao

A mudanca principal sera em `index.html`, preservando o protocolo atual do
WebSocket e os mapas de filtros de `main.py`. A interface deve separar estado,
renderizacao e transporte com funcoes JavaScript pequenas:

- estado dos filtros ativos;
- renderizacao da trilha inferior;
- aplicacao, edicao e remocao de filtro;
- envio do estado ao servidor;
- atualizacao dos estados visuais;
- tratamento de mensagens binarias e erros.

O protocolo numerico existente deve permanecer compativel. Nao sera introduzido
framework frontend nem dependencia adicional para esta reformulacao.

## Testes e validacao

Antes da implementacao, criar testes focados no comportamento da interface ou
funcoes puras equivalentes para:

1. renderizar uma lista de filtros ativos com seus parametros;
2. remover o primeiro, um item do meio e o ultimo filtro;
3. preservar a ordem dos filtros restantes;
4. gerar o payload WebSocket correto depois da remocao;
5. restaurar o estado sem filtros;
6. impedir que o clique no `X` abra o editor do item;
7. validar parametros invalidos sem enviar dados incompletos.

A validacao manual deve cobrir:

- imagem carregada em notebook;
- camera iniciada e encerrada;
- cadeia com pelo menos quatro filtros;
- remocao de filtro do meio usando somente o `X`;
- estados vazio, carregando, processando, erro e resultado;
- navegacao completa por teclado;
- larguras de notebook menores sem sobreposicao.

Tambem executar compilacao Python e os testes existentes para confirmar que a
reformulacao nao alterou o servidor ou o processamento.

## Escopo

### Incluido

- reformulacao visual completa de `index.html`;
- nova hierarquia de layout;
- nova paleta e tipografia;
- agrupamento e apresentacao dos filtros;
- trilha de filtros ativos com remocao por `X`;
- exibicao de parametros;
- estados de conexao, processamento, erro e vazio;
- melhorias basicas de acessibilidade e responsividade para notebook;
- testes focados no estado e na remocao de filtros.

### Fora do escopo

- troca do framework ou criacao de um bundle frontend;
- reescrita dos algoritmos de processamento;
- alteracao do protocolo WebSocket numerico;
- experiencia dedicada para celular;
- redesign do backend ou dos algoritmos de medicao;
- novas operacoes de processamento nao existentes.

## Criterios de aceite

- O usuario encontra claramente como carregar uma imagem ou iniciar a camera.
- A imagem e o resultado ocupam a area principal da tela.
- Os filtros disponiveis ficam agrupados e legiveis.
- Cada filtro aplicado tem um botao `X` visivel e acessivel.
- Remover qualquer filtro reaplica corretamente os demais na ordem original.
- Remover todos os filtros restaura a imagem original.
- Nenhum controle depende de clique do meio ou Shift.
- A tela comunica conexao, carregamento, processamento, erro e estado vazio.
- A interface permanece utilizavel em notebooks menores sem sobreposicao.
- O protocolo e o processamento Python continuam funcionando sem regressao.
