import numpy as np
import matplotlib.pyplot as plt
import cv2
import time

#
def escala_cinza(img):
    if len(img.shape) > 2:
        img = img[0:-1, 0:-1, 0]/3 + img[0:-1, 0:-1, 1]/3 + img[0:-1, 0:-1, 2]/3
    return img.astype(np.uint8)
#
def negativo(img):
    return 255-img

def threshold(img, t=0):
    return ((img >= t)*255).astype(np.uint8)

def normalizacao(img, minVal=0, maxVal=255):
    a = img.min()
    b = img.max()
    img = (img-a)*((maxVal-minVal)/(b-a))+minVal
    return img.astype(np.uint8)
#
def histograma(img, histTitle='', norm=False, cum=False, plot=True):
    if plot:
        fig, ax = plt.subplots()
        ax.set_title("Histograma " + histTitle)
        fig.canvas.manager.set_window_title("Histograma " + histTitle)
    hist, _ = np.histogram(img.flatten(), bins=256, range=(0, 256))
    if norm:
        hist = hist/hist.sum()
    if cum:
        hist = hist.cumsum()
    if plot:
        ax.bar(np.arange(256), hist)
        fig.canvas.draw()
        img_plot = np.array(fig.canvas.renderer.buffer_rgba())
        plt.close()
        return cv2.cvtColor(img_plot, cv2.COLOR_RGBA2BGR)
    return hist
#
def Otsu(img):
    hist = histograma(img, plot=False)
    total = img.shape[0]*img.shape[1]

    pSum = 0
    for key, val in enumerate(hist):
        pSum += key*val

    sumB, wB, wF = 0, 0, 0

    varMax, t = 0, 0
    # sortedItems = hist.sort()
    for key in range(255, -1, -1):
        val = hist[key]
        wB += val

        wF = total - wB
        if wF == 0:
            break

        sumB += key*val
        mB = sumB/wB
        mF = (pSum-sumB)/wF

        varBetween = wB*wF*(mB-mF)*(mB-mF)

        if varBetween > varMax:
            varMax = varBetween
            t = key
    return threshold(img, t)

def kernelPass(func, **kwargs):
    img = kwargs.get('img')
    newImg = kwargs.get('newImg')
    pty = kwargs.get('pty')
    ptx = kwargs.get('ptx')
    halfW = kwargs.get('halfW')
    extraAdd = kwargs.get('extraAdd')

    start = time.time()
    while pty <= img.shape[0]-(halfW+extraAdd):
        while ptx <= img.shape[1]-(halfW+extraAdd):
            kwargs['ptx'] = ptx
            kwargs['pty'] = pty
            func(**kwargs)
            ptx += 1
        ptx = halfW
        pty += 1
    print(f'Kernel pass: {time.time()-start}s')
    return normalizacao
    (newImg)
#
def neighboorMean(img, window):
    newImg = np.zeros(img.shape)
    halfW = window >> 1
    ptx = halfW
    pty = halfW
    extraAdd = 1 if window & 1 else 0

    def func(**kwargs):
        img = kwargs.get('img')
        newImg = kwargs.get('newImg')
        pty = kwargs.get('pty')
        ptx = kwargs.get('ptx')
        halfW = kwargs.get('halfW')

        if len(img.shape) > 2:
            newImg[pty, ptx, 0] = np.mean(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd, 0])
            newImg[pty, ptx, 1] = np.mean(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd, 1])
            newImg[pty, ptx, 2] = np.mean(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd, 2])
        else:
            newImg[pty, ptx] = np.mean(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd])
    
    return kernelPass(func, img=img, newImg=newImg, pty=pty, ptx=ptx, halfW=halfW, extraAdd=extraAdd)
#
def neighboorMedian(img, window):
    newImg = np.zeros(img.shape)
    halfW = window >> 1
    ptx = halfW
    pty = halfW
    extraAdd = 1 if window & 1 else 0

    def func(**kwargs):
        img = kwargs.get('img')
        newImg = kwargs.get('newImg')
        pty = kwargs.get('pty')
        ptx = kwargs.get('ptx')
        halfW = kwargs.get('halfW')

        if len(img.shape) > 2:
            newImg[pty, ptx, 0] = np.median(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd, 0])
            newImg[pty, ptx, 1] = np.median(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd, 1])
            newImg[pty, ptx, 2] = np.median(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd, 2])
        else:
            newImg[pty, ptx] = np.median(img[pty-halfW:pty+halfW+extraAdd, ptx-halfW:ptx+halfW+extraAdd])
    
    return kernelPass(func, img=img, newImg=newImg, pty=pty, ptx=ptx, halfW=halfW, extraAdd=extraAdd)
#
def Canny(img, t1, t2):
    return cv2.Canny(img, t1, t2)
#
def erode(img, kernelSize):
    kernel = np.ones((kernelSize, kernelSize), np.uint8)
    return cv2.erode(img, kernel)
#
def dilate(img, kernelSize):
    kernel = np.ones((kernelSize, kernelSize), np.uint8)
    return cv2.dilate(img, kernel)
#
def opening(img, kernelSize):
    kernel = np.ones((kernelSize, kernelSize), np.uint8)
    img1 = cv2.erode(img, kernel)
    return cv2.dilate(img1, kernel)
#
def closing(img, kernelSize):
    kernel = np.ones((kernelSize, kernelSize), np.uint8)
    img1 = cv2.dilate(img, kernel)
    return cv2.erode(img1, kernel)

def insideImg(img, pos):
    return pos[0] >= 0 and pos[0] < img.shape[0] and pos[1] >= 0 and pos[1] < img.shape[1]

def areaVideo(img, pixelSize=1):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    result = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        area = cv2.contourArea(contour) * pixelSize
        x, y = contour[0][0]
        cv2.putText(result, f'{area:.1f}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    return result

def area(img, pixelSize=1):
    poss = []
    mask = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            if img[row, col] != 0 and mask[row, col, 1] == 0:
                seed = (row, col)
                count = 0
                q = [seed]
                while(len(q) > 0):
                    pos = q.pop(0)
                    if insideImg(img, pos) and img[pos[0], pos[1]] != 0 and mask[pos[0], pos[1], 1] == 0:
                        mask[pos[0], pos[1]] = [255, 255, 255]
                        count += 1
                        q.append((pos[0],   pos[1]+1))
                        q.append((pos[0],   pos[1]-1))
                        q.append((pos[0]+1, pos[1]))
                        q.append((pos[0]-1, pos[1]))
                poss.append((row, col, (count)*pixelSize))
    for pos in poss:
        mask = cv2.putText(mask, f'{pos[2]}', (pos[1], pos[0]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(0, 0, 255))
    return mask

def neighboors(img, pos):
    mask = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]], np.uint8)
    if insideImg(img, pos):
        mask[1, 1] = img[pos[0], pos[1]]
    if pos[0]-1 >= 0:
        mask[0, 1] = img[pos[0]-1, pos[1]]
    if pos[1]-1 >= 0:
        mask[1, 0] = img[pos[0], pos[1]-1]
    if pos[0]+1 < img.shape[0]:
        mask[2, 1] = img[pos[0]+1, pos[1]]
    if pos[1]+1 < img.shape[1]:
        mask[1, 2] = img[pos[0], pos[1]+1]

    if pos[0]-1 >= 0 and pos[1]-1 >= 0:
        mask[0, 0] = img[pos[0]-1, pos[1]-1]
    if pos[0]-1 >= 0 and pos[1]+1 < img.shape[1]:
        mask[0, 2] = img[pos[0]-1, pos[1]+1]
    if pos[0]+1 < img.shape[0] and pos[1]-1 >= 0:
        mask[2, 0] = img[pos[0]+1, pos[1]-1]
    if pos[0]+1 < img.shape[0] and pos[1]+1 < img.shape[1]:
        mask[2, 2] = img[pos[0]+1, pos[1]+1]
    
    return mask.flatten()

def perimeterVideo(img, pixelSize=1):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    result = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        perimeter = cv2.arcLength(contour, True) * pixelSize
        x, y = contour[0][0]
        cv2.putText(result, f'{perimeter:.1f}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    return result

def perimeter(img, pixelSize=1):
    poss = []
    mask = np.zeros((img.shape[0], img.shape[1], 3))
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            if img[row, col] != 0 and mask[row, col, 0] == 0:
                seed = (row, col)
                count = 0
                q = [seed]
                while(len(q) > 0):
                    pos = q.pop(0)
                    if insideImg(img, pos) and img[pos[0], pos[1]] != 0 and mask[pos[0], pos[1], 0] == 0:
                        mask[pos[0], pos[1]] = [255, 255, 255]
                        if any([pixel == 0 for pixel in neighboors(img, pos)]):
                            count += 1
                        q.append((pos[0],   pos[1]+1))
                        q.append((pos[0],   pos[1]-1))
                        q.append((pos[0]+1, pos[1]))
                        q.append((pos[0]-1, pos[1]))
                poss.append((row, col, count*pixelSize))
    for pos in poss:
        mask = cv2.putText(mask, f'{pos[2]}', (pos[1], pos[0]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(0, 0, 255))
    return mask

def diameterVideo(img, pixelSize=1):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    result = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for contour in contours:
        x, y = contour[0][0]
        _,radius = cv2.minEnclosingCircle(contour)
        cv2.putText(result, f'{2*radius*pixelSize:.1f}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    return result

def diameter(img, pixelSize=1):
    mask = np.zeros((img.shape[0], img.shape[1], 3))
    borders = []
    diameters = []
    textPos = []
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            if img[row, col] != 0 and mask[row, col, 0] == 0:
                seed = (row, col)
                q = [seed]
                border = []
                while(len(q) > 0):
                    pos = q.pop(0)
                    if insideImg(img, pos) and img[pos[0], pos[1]] != 0 and mask[pos[0], pos[1], 0] == 0:
                        mask[pos[0], pos[1]] = [255, 255, 255]
                        if any([pixel == 0 for pixel in neighboors(img, pos)]):
                            border.append(pos)
                        q.append((pos[0],   pos[1]+1))
                        q.append((pos[0],   pos[1]-1))
                        q.append((pos[0]+1, pos[1]))
                        q.append((pos[0]-1, pos[1]))
                borders.append(border)
                textPos.append((row, col))
    for border in borders:
        maxDiameter = 0
        for i in range(len(border)):
            for j in range(i, len(border)):
                maxDiameter = max(maxDiameter, pixelSize*np.sqrt((border[i][0]-border[j][0])**2 + (border[i][1]-border[j][1])**2))
        diameters.append(maxDiameter)
    for i, diameter in enumerate(diameters):
        mask = cv2.putText(mask, f'{diameter:.1f}', (textPos[i][1], textPos[i][0]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(0, 0, 255))
    return mask

def objectsVideo(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    result = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    i = 1
    for contour in contours:
        x, y = contour[0][0]
        cv2.putText(result, f'{i}', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        i += 1

    return result


def _component_detections(mask, min_area):
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    border_labels = set(labels[0, :]) | set(labels[-1, :]) | set(labels[:, 0]) | set(labels[:, -1])
    detections = []
    for label in range(1, count):
        area = int(stats[label, cv2.CC_STAT_AREA])
        if area < min_area or label in border_labels:
            continue
        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        object_width = int(stats[label, cv2.CC_STAT_WIDTH])
        object_height = int(stats[label, cv2.CC_STAT_HEIGHT])
        center = tuple(float(value) for value in centroids[label])
        detections.append({
            'bbox': (x, y, object_width, object_height),
            'center': center,
        })
    return detections


def detect_objects(img, min_area=400):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) > 2 else img
    _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    candidates = [
        _component_detections(thresholded, min_area),
        _component_detections(cv2.bitwise_not(thresholded), min_area),
    ]
    detections = max(candidates, key=lambda items: (len(items), sum(item['bbox'][2] * item['bbox'][3] for item in items)))
    annotated = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for detection in detections:
        x, y, width, height = detection['bbox']
        cv2.rectangle(annotated, (x, y), (x + width, y + height), (0, 255, 0), 2)
    return annotated, detections


def match_detections(previous, current, max_distance=80):
    unmatched = set(range(len(previous)))
    matched = []
    previous_numbers = [
        int(item['id'].split('-')[-1])
        for item in previous
        if str(item.get('id', '')).startswith('object-') and item['id'].split('-')[-1].isdigit()
    ]
    next_id = max(previous_numbers, default=0) + 1
    for detection in current:
        best_index = None
        best_distance = max_distance
        for index in unmatched:
            previous_center = np.array(previous[index]['center'])
            current_center = np.array(detection['center'])
            distance = float(np.linalg.norm(previous_center - current_center))
            if distance <= best_distance:
                best_index = index
                best_distance = distance
        if best_index is None:
            detection_id = f'object-{next_id}'
            next_id += 1
        else:
            detection_id = previous[best_index]['id']
            unmatched.remove(best_index)
        matched.append({**detection, 'id': detection_id})
    return matched

def objects(img):
    count = 0
    poss = []
    mask = np.zeros((img.shape[0], img.shape[1], 3))
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            if img[row, col] != 0 and mask[row, col, 0] == 0:
                seed = (row, col)
                count += 1
                q = [seed]
                while(len(q) > 0):
                    pos = q.pop(0)
                    if insideImg(img, pos) and img[pos[0], pos[1]] != 0 and mask[pos[0], pos[1], 0] == 0:
                        mask[pos[0], pos[1]] = [255, 255, 255]
                        q.append((pos[0],   pos[1]+1))
                        q.append((pos[0],   pos[1]-1))
                        q.append((pos[0]+1, pos[1]))
                        q.append((pos[0]-1, pos[1]))
                poss.append((row, col, count))
    for pos in poss:
        mask = cv2.putText(mask, f'{pos[2]}', (pos[1], pos[0]+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color=(0, 0, 255))
    return mask


def trackVideo(img, previous_detections=None):
    annotated, detections = detect_objects(img)
    return annotated, match_detections(previous_detections or [], detections)

def videoMean(img, kernelSize):
    return cv2.filter2D(img,-1,np.ones((kernelSize, kernelSize), np.float32)/(kernelSize*kernelSize)).astype(np.uint8)

def videoMedian(img, kernelSize):
    return cv2.medianBlur(img, kernelSize)