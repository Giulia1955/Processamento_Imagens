# Image Workshop

## Dependencias

Use Python 3 e instale as dependencias do projeto:

```bash
python -m pip install -r requirements.txt
```

O filtro de rastreamento usa `ultralytics` e carrega o modelo YOLO sob demanda.
O arquivo padrao e `yolo11n.pt`; ele pode ser substituido definindo
`YOLO_MODEL_PATH` antes de iniciar o servidor:

```bash
export YOLO_MODEL_PATH=/caminho/para/modelo.pt
python main.py
```

Na primeira execucao, o Ultralytics pode baixar os pesos do modelo. As classes
exibidas e contadas sao limitadas ao vocabulario do modelo usado. O total
mostrado e a quantidade de deteccoes no frame atual; os IDs servem somente para
manter continuidade entre frames e identificar objetos novos.

As funcoes Area, Perimeter, Diameter e Object counting para imagens binarias
usam componentes conectados. Cada componente e medido separadamente.
