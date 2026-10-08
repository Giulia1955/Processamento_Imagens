import numpy as np
import matplotlib.pyplot as plt
import cv2
import time
import os

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

def _binary_mask(img):
    if img is None or not hasattr(img, 'shape') or len(img.shape) < 2:
        raise ValueError('A imagem deve ter pelo menos duas dimensoes')
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    unique_vals = np.unique(img)
    if len(unique_vals) <= 2 and (0 in unique_vals or 255 in unique_vals):
        return np.where(img != 0, 255, 0).astype(np.uint8)
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if np.mean(thresh == 255) > 0.5:
        thresh = cv2.bitwise_not(thresh)
    return thresh

def extract_components(img):
    binary = _binary_mask(img)
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, 8)
    components = []
    valid_labels = range(1, count)
    if count > 150:
        areas = stats[1:, cv2.CC_STAT_AREA]
        sorted_indices = np.argsort(-areas)[:100]
        valid_labels = [idx + 1 for idx in sorted_indices]

    for label in valid_labels:
        x = int(stats[label, cv2.CC_STAT_LEFT])
        y = int(stats[label, cv2.CC_STAT_TOP])
        width = int(stats[label, cv2.CC_STAT_WIDTH])
        height = int(stats[label, cv2.CC_STAT_HEIGHT])
        if width <= 0 or height <= 0:
            continue
        sub_labels = labels[y:y+height, x:x+width]
        sub_mask = np.zeros((height + 2, width + 2), dtype=np.uint8)
        sub_mask[1:-1, 1:-1] = (sub_labels == label).astype(np.uint8) * 255
        contours, _ = cv2.findContours(sub_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            continue
        contour = max(contours, key=cv2.contourArea)
        contour[:, 0, 0] += x - 1
        contour[:, 0, 1] += y - 1
        _, radius = cv2.minEnclosingCircle(contour)
        components.append({
            'label': label,
            'mask': sub_mask[1:-1, 1:-1],
            'contour': contour,
            'area': int(stats[label, cv2.CC_STAT_AREA]),
            'perimeter': float(cv2.arcLength(contour, True)),
            'diameter': float(radius * 2),
            'bbox': (x, y, width, height),
            'center': tuple(float(value) for value in centroids[label]),
        })
    return components

def _annotated_components(img, value_name, pixel_size=1):
    pixel_size = float(pixel_size) if (pixel_size is not None and pixel_size > 0) else 1.0
    binary = _binary_mask(img)
    if len(img.shape) > 2 and img.shape[2] == 3:
        result = img.copy()
    else:
        result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    for number, component in enumerate(extract_components(binary), start=1):
        x, y, _, _ = component['bbox']
        if value_name == 'number':
            text = str(number)
        else:
            text = f'{component[value_name] * pixel_size:.1f}'
        cv2.putText(result, text, (x, max(y + 15, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    return result

def areaVideo(img, pixelSize=1):
    return area(img, pixelSize)

def area(img, pixelSize=1):
    return _annotated_components(img, 'area', pixelSize)

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
    return perimeter(img, pixelSize)

def perimeter(img, pixelSize=1):
    return _annotated_components(img, 'perimeter', pixelSize)

def diameterVideo(img, pixelSize=1):
    return diameter(img, pixelSize)

def diameter(img, pixelSize=1):
    return _annotated_components(img, 'diameter', pixelSize)

def objectsVideo(img, detector=None):
    if detector is not None:
        return detect_objects(img, detector=detector)
    return detect_objects(img)


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


class YoloDetector:
    def __init__(self, model_path=None, confidence=0.25):
        self.model_path = model_path or os.environ.get('YOLO_MODEL_PATH', 'yolo11n.pt')
        self.confidence = confidence
        self._model = None

    def detect(self, frame):
        if self._model is None:
            try:
                from ultralytics import YOLO
                self._model = YOLO(self.model_path)
            except Exception as error:
                raise RuntimeError(f'Nao foi possivel carregar o modelo YOLO: {error}') from error
        try:
            result = self._model(frame, conf=self.confidence, verbose=False)[0]
            names = result.names
            detections = []
            for box in result.boxes:
                coordinates = box.xyxy[0].tolist()
                x1, y1, x2, y2 = (int(value) for value in coordinates)
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                detections.append({
                    'class_name': names[class_id],
                    'confidence': confidence,
                    'bbox': (x1, y1, x2 - x1, y2 - y1),
                    'center': ((x1 + x2) / 2, (y1 + y2) / 2),
                    'area': max(0, x2 - x1) * max(0, y2 - y1),
                })
            return detections
        except Exception as error:
            raise RuntimeError(f'Falha na inferencia YOLO: {error}') from error

def _annotate_detections(img, detections):
    annotated = img.copy() if (len(img.shape) > 2 and img.shape[2] == 3) else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for detection in detections:
        x, y, width, height = detection['bbox']
        label = f"{detection['class_name']} {detection['confidence']:.2f}"
        cv2.rectangle(annotated, (x, y), (x + width, y + height), (0, 255, 0), 2)
        cv2.putText(annotated, label, (x, max(y - 6, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
    cv2.putText(annotated, f'Objetos: {len(detections)}', (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return annotated

def detect_objects(img, min_area=400, detector=None):
    if detector is not None:
        detections = detector.detect(img)
        return _annotate_detections(img, detections), detections
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
    return _annotated_components(img, 'number', 1)


def trackVideo(img, previous_detections=None, detector=None):
    annotated, detections = detect_objects(img, detector=detector)
    return annotated, match_detections(previous_detections or [], detections)

def videoMean(img, kernelSize):
    return cv2.filter2D(img,-1,np.ones((kernelSize, kernelSize), np.float32)/(kernelSize*kernelSize)).astype(np.uint8)

def videoMedian(img, kernelSize):
    return cv2.medianBlur(img, kernelSize)