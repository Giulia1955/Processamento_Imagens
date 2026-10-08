import unittest

import cv2
import numpy as np

import main
import funcs
from funcs import detect_objects, match_detections


class ProcessVideoTests(unittest.TestCase):
    def tearDown(self):
        main.filters = []

    def test_tracking_without_previous_detections_keeps_frame_shape(self):
        frame = np.zeros((16, 16, 3), dtype=np.uint8)
        main.filters = [[16, 0, 0]]

        result = main.processVideo(frame)

        self.assertTrue(np.array_equal(result, frame))

    def test_detect_objects_finds_two_separate_components(self):
        frame = np.zeros((120, 160), dtype=np.uint8)
        cv2.rectangle(frame, (10, 20), (39, 59), 255, -1)
        cv2.rectangle(frame, (100, 70), (139, 109), 255, -1)

        annotated, detections = detect_objects(frame, min_area=100)

        self.assertEqual(len(detections), 2)
        self.assertEqual(annotated.shape, (120, 160, 3))

    def test_match_detections_preserves_ids_and_assigns_new_object_id(self):
        previous = [
            {'id': 'object-1', 'bbox': (10, 10, 20, 20), 'center': (20, 20)},
        ]
        current = [
            {'bbox': (13, 12, 20, 20), 'center': (23, 22)},
            {'bbox': (100, 100, 20, 20), 'center': (110, 110)},
        ]

        matched = match_detections(previous, current, max_distance=20)

        self.assertEqual([item['id'] for item in matched], ['object-1', 'object-2'])

    def test_match_detections_does_not_reuse_an_unmatched_previous_id(self):
        previous = [
            {'id': 'object-1', 'bbox': (10, 10, 20, 20), 'center': (20, 20)},
            {'id': 'object-3', 'bbox': (100, 100, 20, 20), 'center': (110, 110)},
        ]
        current = [
            {'bbox': (13, 12, 20, 20), 'center': (23, 22)},
            {'bbox': (200, 200, 20, 20), 'center': (210, 210)},
        ]

        matched = match_detections(previous, current, max_distance=20)

        self.assertEqual([item['id'] for item in matched], ['object-1', 'object-4'])

    def test_process_video_returns_all_tracking_detections(self):
        frame = np.zeros((120, 160, 3), dtype=np.uint8)
        cv2.rectangle(frame, (10, 20), (39, 59), (255, 255, 255), -1)
        cv2.rectangle(frame, (100, 70), (139, 109), (255, 255, 255), -1)
        main.filters = [[16, 0, 0]]

        _, detections = main.processVideo(frame, return_detections=True)

        self.assertEqual(len(detections), 2)

    def test_extract_components_returns_independent_measurements(self):
        image = np.zeros((80, 100), dtype=np.uint8)
        image[10:20, 10:20] = 255
        image[40:60, 60:80] = 255

        components = funcs.extract_components(image)

        self.assertEqual(len(components), 2)
        self.assertEqual(sorted(item['area'] for item in components), [100, 400])
        self.assertTrue(all(item['perimeter'] > 0 for item in components))
        self.assertTrue(all(item['diameter'] > 0 for item in components))

    def test_measurement_filters_return_annotated_bgr_images(self):
        image = np.zeros((30, 30), dtype=np.uint8)
        image[5:15, 5:15] = 255

        for operation in (funcs.area, funcs.perimeter, funcs.diameter, funcs.objects):
            result = operation(image)
            self.assertEqual(result.shape, (30, 30, 3))
            self.assertEqual(result.dtype, np.uint8)

    def test_detect_objects_annotates_and_counts_detector_results(self):
        class FakeDetector:
            def detect(self, frame):
                return [
                    {'class_name': 'person', 'confidence': 0.91, 'bbox': (2, 3, 10, 20), 'center': (7, 13)},
                    {'class_name': 'cell phone', 'confidence': 0.84, 'bbox': (30, 10, 8, 12), 'center': (34, 16)},
                ]

        frame = np.zeros((50, 60, 3), dtype=np.uint8)
        annotated, detections = detect_objects(frame, detector=FakeDetector())

        self.assertEqual(annotated.shape, frame.shape)
        self.assertEqual([item['class_name'] for item in detections], ['person', 'cell phone'])
        self.assertEqual(len(detections), 2)

    def test_track_video_keeps_detector_classes_and_assigns_ids(self):
        class FakeDetector:
            def detect(self, frame):
                return [
                    {'class_name': 'person', 'confidence': 0.91, 'bbox': (2, 3, 10, 20), 'center': (7, 13)},
                    {'class_name': 'cell phone', 'confidence': 0.84, 'bbox': (30, 10, 8, 12), 'center': (34, 16)},
                ]

        frame = np.zeros((50, 60, 3), dtype=np.uint8)
        annotated, detections = funcs.trackVideo(frame, detector=FakeDetector())

        self.assertEqual(annotated.shape, frame.shape)
        self.assertEqual([item['id'] for item in detections], ['object-1', 'object-2'])
        self.assertEqual(len(detections), 2)

    def test_video_measurement_filters_work_on_color_frames(self):
        color_frame = np.zeros((100, 100, 3), dtype=np.uint8)
        color_frame[20:40, 20:40] = (255, 255, 255)

        for operation in (funcs.areaVideo, funcs.perimeterVideo, funcs.diameterVideo):
            result = operation(color_frame)
            self.assertEqual(result.shape, color_frame.shape)
            self.assertEqual(result.dtype, np.uint8)

    def test_process_video_counting_filter_detects_and_returns_objects(self):
        class FakeDetector:
            def detect(self, frame):
                return [
                    {'class_name': 'person', 'confidence': 0.95, 'bbox': (5, 5, 20, 30), 'center': (15, 20), 'area': 600},
                    {'class_name': 'cell phone', 'confidence': 0.88, 'bbox': (40, 40, 10, 15), 'center': (45, 47), 'area': 150},
                ]

        frame = np.zeros((80, 80, 3), dtype=np.uint8)
        main.filters = [[14, 0, 0]]

        annotated, detections = main.processVideo(frame, return_detections=True, detector=FakeDetector())

        self.assertEqual(annotated.shape, frame.shape)
        self.assertEqual(len(detections), 2)
        self.assertEqual([d['class_name'] for d in detections], ['person', 'cell phone'])

    def test_measurement_filters_handle_zero_or_negative_pixel_size(self):
        image = np.zeros((40, 40), dtype=np.uint8)
        image[10:20, 10:20] = 255

        for operation in (funcs.area, funcs.perimeter, funcs.diameter):
            result_zero = operation(image, pixelSize=0)
            result_neg = operation(image, pixelSize=-5)
            self.assertEqual(result_zero.shape, (40, 40, 3))
            self.assertEqual(result_neg.shape, (40, 40, 3))

    def test_extract_components_fast_on_noisy_image(self):
        import time
        np.random.seed(42)
        noise = (np.random.rand(200, 200) > 0.6).astype(np.uint8) * 255
        start = time.time()
        comps = funcs.extract_components(noise)
        duration = time.time() - start
        self.assertLess(duration, 0.5)
        self.assertGreater(len(comps), 0)


if __name__ == '__main__':
    unittest.main()
