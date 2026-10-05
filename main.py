import cv2
import numpy as np
import websockets
import asyncio
import json
from funcs import *


def passFunc(img, *args, **kwargs):
    return img

functions = {
    0: escala_cinza,   
    1: negativo,
    2: Otsu,
    3: neighboorMean,
    4: neighboorMedian,
    5: Canny,
    6: erode,
    7: dilate,
    8: opening,
    9: closing,
    10: histograma,   
    11: area,
    12: perimeter,
    13: diameter,
    14: objects,
    15: threshold,
    16: passFunc
}

functionsVideo = {
    0: escala_cinza,   
    1: negativo,
    2: Otsu,
    3: videoMean,
    4: videoMedian,
    5: Canny,
    6: erode,
    7: dilate,
    8: opening,
    9: closing,
    10: passFunc,
    11: areaVideo,
    12: perimeterVideo,
    13: diameterVideo,
    14: objectsVideo,
    15: threshold,
    16: trackVideo
}

filters = []

def setFilters(content):
    global filters
    filters = []
    for func, p1, p2 in [content[n:n+3] for n in range(0, len(content), 3)]:
        filters.append([func, p1, p2])

def process(img):
    for filter_idx, p1, p2 in filters:
        if filter_idx == 5:
            img = functions[filter_idx](img, p1, p2)
        elif filter_idx == 10:
            img = functions[filter_idx](img, norm=(p2 == 1), cum=(p1 == 1))
        elif (3 <= filter_idx <= 13) or filter_idx == 15:
            img = functions[filter_idx](img, p1)
        else:
            img = functions[filter_idx](img)
    return img

def processVideo(img, previous_detections=None, return_detections=False):
    detections = []
    for filter_idx, p1, p2 in filters:
        if filter_idx == 5:
            img = functionsVideo[filter_idx](img, p1, p2)
        elif filter_idx == 10:
            img = functionsVideo[filter_idx](img, norm=(p2 == 1), cum=(p1 == 1))
        elif filter_idx == 16:
            img, detections = functionsVideo[filter_idx](img, previous_detections)
        elif (3 <= filter_idx <= 13) or filter_idx == 15:
            img = functionsVideo[filter_idx](img, p1)
        else:
            img = functionsVideo[filter_idx](img)
    if return_detections:
        return img, detections
    return img

async def handler(websocket):
    originalImg = None
    img = None
    imgSet = False
    streamType = None
    previous_detections = []

    while True:
        try:
            data = await websocket.recv()
        except websockets.exceptions.ConnectionClosed:
            break

        typeByte = data[0]
        content = data[1:]

        if typeByte == 0:
            setFilters(np.frombuffer(content, np.uint8))
            if imgSet and originalImg is not None:
                if len(filters) > 0:
                    if streamType == 1:
                        img = process(originalImg.copy())
                    elif streamType == 2:
                        img, previous_detections = processVideo(
                            originalImg.copy(), previous_detections, True,
                        )
                    _, buffer = cv2.imencode('.png', img)
                    await websocket.send(buffer.tobytes())
                    if streamType == 2 and any(filter_idx == 16 for filter_idx, _, _ in filters):
                        await websocket.send(json.dumps({
                            'type': 'detections',
                            'objects': previous_detections,
                        }))
                else:
                    _, buffer = cv2.imencode('.png', originalImg)
                    await websocket.send(buffer.tobytes())

        elif typeByte == 1:
            streamType = 1
            previous_detections = []
            decodedData = np.frombuffer(content, np.uint8)
            img = cv2.imdecode(decodedData, cv2.IMREAD_COLOR)

            originalImg = img.copy()
            try:
                img = process(img)
            except Exception as e:
                print(f"Erro no processamento da imagem: {e}")
            imgSet = True
            _, buffer = cv2.imencode('.png', img)
            await websocket.send(buffer.tobytes())

        else:
            streamType = 2
            decodedData = np.frombuffer(content, np.uint8)
            img = cv2.imdecode(decodedData, cv2.IMREAD_COLOR)

            if img is not None:
                originalImg = img.copy()
                try:
                    img, previous_detections = processVideo(
                        img, previous_detections, True,
                    )
                except Exception as e:
                    print(f"Erro no processamento de vídeo: {e}")

                imgSet = True
                _, buffer = cv2.imencode('.png', img)
                await websocket.send(buffer.tobytes())
                if any(filter_idx == 16 for filter_idx, _, _ in filters):
                    await websocket.send(json.dumps({
                        'type': 'detections',
                        'objects': previous_detections,
                    }))
async def main():
    async with websockets.serve(handler, "localhost", 8080, max_size=2**32, max_queue=100):
        print("Servidor WebSocket rodando em ws://localhost:8080")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())