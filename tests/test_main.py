import unittest

import cv2
import numpy as np

import main
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


if __name__ == '__main__':
    unittest.main()
