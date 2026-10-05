# Deteccao de multiplos objetos na camera

## Objetivo
Substituir o rastreamento de um unico objeto por deteccao de multiplos objetos em cada frame da camera e tocar `detection.mp3` uma vez quando um novo objeto surgir.

## Decisoes
- O filtro Tracking usara componentes conectados/contornos em cada frame, sem manter um `TrackerKCF` unico.
- Cada objeto detectado recebe uma caixa e um identificador estavel por proximidade entre frames.
- O servidor preserva as mensagens binarias PNG existentes e envia metadados de deteccao em uma mensagem JSON separada.
- O navegador compara os IDs atuais com os IDs do frame anterior e toca `detection.mp3` somente para IDs novos.
- A reproducao de audio ocorre apos interacao do usuario, respeitando as politicas do navegador.
- O processamento estatico de imagens e os demais filtros permanecem inalterados.

## Criterios de aceite
- Dois ou mais objetos visiveis podem ser marcados no mesmo frame.
- Um objeto persistente nao reinicia o audio a cada frame.
- Um objeto novo dispara uma reproducao do arquivo local.
- Quando todos os objetos somem, a proxima aparicao e considerada nova.
- Falhas de audio nao interrompem o processamento de video.
