"""
IBVAP Real Object Tracking Engine
Implements spatial IoU & centroid multi-object tracking to assign persistent Track IDs,
record trajectory history, and measure object velocity/loitering over consecutive video frames.
"""

import time
import numpy as np


class TrackedObject:
    def __init__(self, track_id, detection, timestamp=None):
        self.track_id = track_id
        self.class_name = detection['class_name']
        self.is_person = detection.get('is_person', False)
        self.is_vehicle = detection.get('is_vehicle', False)
        self.confidence = detection['confidence']
        self.box = detection['box']  # [x1, y1, x2, y2]
        self.center = detection['center']  # (cx, cy)
        
        now = timestamp or time.time()
        self.first_seen = now
        self.last_seen = now
        self.history = [(self.center[0], self.center[1], now)]
        self.disappeared_count = 0

        # Security zone states
        self.in_restricted_zone = False
        self.zone_entry_time = None
        self.loitering_alerted = False
        self.intrusion_alerted = False

    def update(self, detection, timestamp=None):
        now = timestamp or time.time()
        self.box = detection['box']
        self.center = detection['center']
        self.confidence = detection['confidence']
        # Dynamically update class and detection type
        self.class_name = detection['class_name']
        self.is_person = detection.get('is_person', False)
        self.is_vehicle = detection.get('is_vehicle', False)
        self.last_seen = now
        self.disappeared_count = 0
        self.history.append((self.center[0], self.center[1], now))
        if len(self.history) > 120:  # Keep last 120 positions
            self.history.pop(0)

    @property
    def duration_seconds(self):
        return max(0.0, self.last_seen - self.first_seen)

    @property
    def zone_duration_seconds(self):
        if self.in_restricted_zone and self.zone_entry_time:
            return max(0.0, self.last_seen - self.zone_entry_time)
        return 0.0

    @property
    def trajectory_direction(self):
        """Calculates rough movement vector from last 10 points."""
        if len(self.history) < 2:
            return "STATIONARY"
        p_start = self.history[0]
        p_end = self.history[-1]
        dx = p_end[0] - p_start[0]
        dy = p_end[1] - p_start[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < 15:
            return "STATIONARY"
        if abs(dx) > abs(dy):
            return "EASTBOUND (RIGHT)" if dx > 0 else "WESTBOUND (LEFT)"
        else:
            return "INBOUND (SOUTH)" if dy > 0 else "OUTBOUND (NORTH)"


def calculate_iou(boxA, boxB):
    """Computes Intersection over Union (IoU) between two bounding boxes [x1, y1, x2, y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    inter_area = max(0.0, xB - xA) * max(0.0, yB - yA)
    boxA_area = max(0.0, boxA[2] - boxA[0]) * max(0.0, boxA[3] - boxA[1])
    boxB_area = max(0.0, boxB[2] - boxB[0]) * max(0.0, boxB[3] - boxB[1])

    union_area = boxA_area + boxB_area - inter_area
    if union_area <= 0:
        return 0.0
    return inter_area / union_area


class RealObjectTracker:
    def __init__(self, max_disappeared=25, iou_threshold=0.25):
        self.next_track_id = 1
        self.tracks = {}  # {track_id: TrackedObject}
        self.max_disappeared = max_disappeared
        self.iou_threshold = iou_threshold

    def update(self, detections, timestamp=None):
        """
        Updates tracked objects with new YOLO detections for the current frame.
        Returns:
            list of active TrackedObject instances
        """
        now = timestamp or time.time()

        if len(detections) == 0:
            for track_id in list(self.tracks.keys()):
                self.tracks[track_id].disappeared_count += 1
                if self.tracks[track_id].disappeared_count > self.max_disappeared:
                    del self.tracks[track_id]
            return list(self.tracks.values())

        if len(self.tracks) == 0:
            for det in detections:
                track = TrackedObject(self.next_track_id, det, now)
                self.tracks[self.next_track_id] = track
                self.next_track_id += 1
            return list(self.tracks.values())

        track_ids = list(self.tracks.keys())
        track_boxes = [self.tracks[tid].box for tid in track_ids]

        # Build IoU Matrix
        num_tracks = len(track_ids)
        num_dets = len(detections)
        iou_matrix = np.zeros((num_tracks, num_dets), dtype=np.float32)

        for t_idx, t_box in enumerate(track_boxes):
            for d_idx, det in enumerate(detections):
                iou_matrix[t_idx, d_idx] = calculate_iou(t_box, det['box'])

        matched_tracks = set()
        matched_dets = set()

        # Greedy match based on highest IoU
        while True:
            if iou_matrix.size == 0:
                break
            max_val = np.max(iou_matrix)
            if max_val < self.iou_threshold:
                break

            t_idx, d_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
            tid = track_ids[t_idx]

            # Update matched track
            self.tracks[tid].update(detections[d_idx], now)
            matched_tracks.add(t_idx)
            matched_dets.add(d_idx)

            # Invalidate row and column
            iou_matrix[t_idx, :] = -1.0
            iou_matrix[:, d_idx] = -1.0

        # Unmatched existing tracks increment disappeared counter
        for t_idx, tid in enumerate(track_ids):
            if t_idx not in matched_tracks:
                self.tracks[tid].disappeared_count += 1
                if self.tracks[tid].disappeared_count > self.max_disappeared:
                    del self.tracks[tid]

        # Unmatched new detections get new track IDs
        for d_idx, det in enumerate(detections):
            if d_idx not in matched_dets:
                track = TrackedObject(self.next_track_id, det, now)
                self.tracks[self.next_track_id] = track
                self.next_track_id += 1

        return list(self.tracks.values())

    def reset(self):
        self.tracks.clear()
        self.next_track_id = 1
