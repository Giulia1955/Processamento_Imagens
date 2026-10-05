import cv2
from funcs import *
import websockets
import asyncio

def passFunc(img, p1=1, p2=1):
    return img

functions = {
    0: grayscale,
    1: negative,
    2: Otsu,
    3: neighboorMean,
    4: neighboorMedian,
    5: Canny,
    6: erode,
    7: dilate,
    8: opening,
    9: closing,
    10: histogram,
    11: area,
    12: perimeter,
    13: diameter,
    14: objects,
    15: threshold,
    16: passFunc
}

functionsVideo = {
    0: grayscale,
    1: negative,
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

tracker = None
filters = []
def setFilters(content):
    global filters, tracker
    tracker = None
    filters = []
    for func, p1, p2 in [content[n:n+3] for n in range(0, len(content), 3)]:
        filters.append([func, p1, p2])

def process(img):
    for filter, p1, p2 in filters:
        if filter == 5:
            img = functions[filter](img, p1, p2)
        elif filter == 10:
            img = functions[filter](img, norm=p2 == 1, cum=p1 == 1)
        elif (filter >= 3 and filter <= 13) or filter == 15:
            img = functions[filter](img, p1)
        else:
            img = functions[filter](img)
    return img

def processVideo(img):
    for filter, p1, p2 in filters:
        if filter == 5:
            img = functionsVideo[filter](img, p1, p2)
        elif filter == 10:
            img = functionsVideo[filter](img, p2 == 1, p1 == 1)
        elif filter == 16 and tracker is not None:
            img = functionsVideo[filter](img, tracker)
        elif (filter >= 3 and filter <= 13) or filter == 15:
            img = functionsVideo[filter](img, p1)
        else:
            img = functionsVideo[filter](img)
    return img

async def handler(websocket):
    global tracker
    originalImg = None
    img = None
    imgSet = False
    streamType = None
    while True:
        data = await websocket.recv()
        typeByte = data[0]
        content = data[1:]

        if typeByte == 0:
            setFilters(np.frombuffer(content, np.uint8))
            if imgSet:
                if len(filters) > 0:
                    if streamType == 1:
                        img = process(originalImg)
                    elif streamType == 1:
                        img = processVideo(originalImg)
                    _, buffer = cv2.imencode('.png', img)
                    await websocket.send(buffer.tobytes())
                else:
                    _, buffer = cv2.imencode('.png', originalImg)
                    await websocket.send(buffer.tobytes())
        elif typeByte == 1:
            streamType = 1
            decodedData = np.frombuffer(content, np.uint8)
            img = cv2.imdecode(decodedData, cv2.IMREAD_COLOR)

            originalImg = img
            try:
                img = process(img)
            except:
                pass
            imgSet = True
            _, buffer = cv2.imencode('.png', img)
            await websocket.send(buffer.tobytes())
        else:
            streamType = 2
            decodedData = np.frombuffer(content, np.uint8)
            img = cv2.imdecode(decodedData, cv2.IMREAD_COLOR)
            
            if tracker is None:
                tracker = cv2.TrackerKCF.create()
                bbox = (img.shape[1]//2-50, img.shape[0]//2-50, 100, 100)
                tracker.init(img, bbox)

            originalImg = img
            try:
                img = processVideo(img)
            except:
                pass
            imgSet = True
            _, buffer = cv2.imencode('.png', img)
            await websocket.send(buffer.tobytes())

async def main():
    async with websockets.serve(handler, "localhost", 8080, max_size=2**32, max_queue=100):
        await asyncio.Future()

asyncio.run(main())