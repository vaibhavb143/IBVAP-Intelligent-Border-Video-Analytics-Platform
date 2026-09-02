"""
IBVAP Real AI Object Detection Engine
Powered by Ultralytics YOLO with ONNX Runtime
Performs real neural inference on video frames and extracts genuine bounding boxes,
object classes, and confidence scores without simulated or mock data.
"""

import os
import urllib.request
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
    'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
    'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
    'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
    'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
    'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
    'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

TARGET_SECURITY_CLASSES = {'person', 'car', 'motorcycle', 'bus', 'truck', 'bicycle', 'backpack', 'suitcase'}


class YOLODetector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(YOLODetector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name="yolov5n.onnx", conf_threshold=0.35, iou_threshold=0.45):
        if self._initialized:
            return

        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.model_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.model_dir, exist_ok=True)
        self.model_path = os.path.join(self.model_dir, model_name)

        self._ensure_model_available()
        self._load_session()
        self._initialized = True

    def _ensure_model_available(self):
        """Downloads the pretrained ONNX weights if not present."""
        if not os.path.exists(self.model_path) or os.path.getsize(self.model_path) < 1000000:
            print("[IBVAP-AI] Downloading official YOLO ONNX weights...")
            url = "https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5n.onnx"
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'IBVAP-Edge-AI/1.0'})
                with urllib.request.urlopen(req, timeout=30) as resp, open(self.model_path, 'wb') as f:
                    f.write(resp.read())
                print(f"[IBVAP-AI] Pretrained YOLO weights downloaded successfully ({os.path.getsize(self.model_path)} bytes).")
            except Exception as e:
                logger.error(f"Failed to download YOLO ONNX model from {url}: {e}")
                raise RuntimeError(f"Could not initialize YOLO detector: {e}")

    def _load_session(self):
        """Initializes ONNX Runtime session."""
        try:
            import onnxruntime as ort
            providers = ['CPUExecutionProvider']
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            self.input_shape = self.session.get_inputs()[0].shape
            print(f"[IBVAP-AI] YOLO ONNX Session loaded on {providers[0]}. Input: {self.input_name}")
        except Exception as e:
            logger.error(f"Error initializing ONNX runtime session: {e}")
            raise

    def _letterbox(self, img_pil, target_size=(640, 640)):
        """Resizes PIL image with aspect ratio preservation and pad borders."""
        w, h = img_pil.size
        tw, th = target_size
        scale = min(tw / w, th / h)
        nw, nh = int(w * scale), int(h * scale)
        resized_img = img_pil.resize((nw, nh), Image.BILINEAR)

        padded_img = Image.new("RGB", target_size, (114, 114, 114))
        pad_x = (tw - nw) // 2
        pad_y = (th - nh) // 2
        padded_img.paste(resized_img, (pad_x, pad_y))

        return padded_img, scale, pad_x, pad_y

    def _nms(self, boxes, scores, iou_threshold):
        """Standard Non-Maximum Suppression."""
        if len(boxes) == 0:
            return []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        areas = (x2 - x1) * (y2 - y1)
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            if order.size == 1:
                break

            xx1 = np.maximum(x1[i], x1[order[1:]])
            yy1 = np.maximum(y1[i], y1[order[1:]])
            xx2 = np.minimum(x2[i], x2[order[1:]])
            yy2 = np.minimum(y2[i], y2[order[1:]])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            inter = w * h

            ovr = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
            inds = np.where(ovr <= iou_threshold)[0]
            order = order[inds + 1]

        return keep

    def detect(self, image_input, conf_threshold=None, target_classes=None):
        """
        Runs real YOLO inference on a PIL Image or NumPy RGB/BGR array.
        Returns:
            list of dicts: [
                {
                    'box': [x1, y1, x2, y2], (in original image coordinates)
                    'normalized_box': [nx1, ny1, nx2, ny2], (0.0 to 1.0)
                    'class_name': str,
                    'class_id': int,
                    'confidence': float,
                    'center': (cx, cy),
                    'is_person': bool,
                    'is_vehicle': bool
                }
            ]
        """
        if conf_threshold is None:
            conf_threshold = self.conf_threshold

        if isinstance(image_input, np.ndarray):
            if image_input.ndim == 2:  # Grayscale
                image_input = np.stack((image_input,) * 3, axis=-1)
            img_pil = Image.fromarray(image_input)
        elif isinstance(image_input, Image.Image):
            img_pil = image_input.convert("RGB")
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        orig_w, orig_h = img_pil.size
        if orig_w == 0 or orig_h == 0:
            return []

        # 1. Preprocessing (Letterbox to 640x640)
        padded_img, scale, pad_x, pad_y = self._letterbox(img_pil, target_size=(640, 640))
        img_np = np.array(padded_img, dtype=np.float32) / 255.0  # Normalize 0-1
        img_tensor = np.transpose(img_np, (2, 0, 1))  # HWC to CHW
        img_tensor = np.expand_dims(img_tensor, axis=0)  # Add batch dim (1, 3, 640, 640)

        # Match input data type (float16 vs float32)
        input_type_str = self.session.get_inputs()[0].type
        if 'float16' in input_type_str:
            img_tensor = img_tensor.astype(np.float16)
        else:
            img_tensor = img_tensor.astype(np.float32)

        # 2. ONNX Inference
        outputs = self.session.run(None, {self.input_name: img_tensor})
        preds = outputs[0].astype(np.float32)  # Ensure float32 for subsequent calculations

        # Handle YOLOv5 / YOLOv8 output shapes
        if preds.shape[1] < preds.shape[2]:  # (1, 84, 8400) -> transpose to (1, 8400, 84)
            preds = np.transpose(preds, (0, 2, 1))

        preds = preds[0]  # Remove batch dim -> (N, 85) or (N, 84)

        # 3. Box & Score Extraction
        if preds.shape[1] == 85:  # YOLOv5 format: [x, y, w, h, obj_conf, cls_0, cls_1, ...]
            boxes = preds[:, :4]
            obj_conf = preds[:, 4]
            cls_probs = preds[:, 5:]
            cls_scores = cls_probs * obj_conf[:, np.newaxis]
            cls_ids = np.argmax(cls_scores, axis=1)
            confidences = np.max(cls_scores, axis=1)
        else:  # YOLOv8 format: [x, y, w, h, cls_0, cls_1, ...]
            boxes = preds[:, :4]
            cls_probs = preds[:, 4:]
            cls_ids = np.argmax(cls_probs, axis=1)
            confidences = np.max(cls_probs, axis=1)

        # Filter by confidence threshold
        mask = confidences >= conf_threshold
        boxes = boxes[mask]
        cls_ids = cls_ids[mask]
        confidences = confidences[mask]

        if len(boxes) == 0:
            return []

        # Convert [cx, cy, w, h] to [x1, y1, x2, y2] in 640x640 space
        cx, cy, w, h = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2
        xyxy = np.column_stack([x1, y1, x2, y2])

        # 4. Apply Non-Maximum Suppression (NMS)
        keep_indices = self._nms(xyxy, confidences, self.iou_threshold)

        detections = []
        for idx in keep_indices:
            cid = int(cls_ids[idx])
            cname = COCO_CLASSES[cid] if cid < len(COCO_CLASSES) else f"class_{cid}"
            conf = float(confidences[idx])

            # If target_classes specified, filter
            if target_classes and cname not in target_classes:
                continue

            # Map coordinates from letterbox (640x640) back to original frame dimensions
            bx1 = (xyxy[idx, 0] - pad_x) / scale
            by1 = (xyxy[idx, 1] - pad_y) / scale
            bx2 = (xyxy[idx, 2] - pad_x) / scale
            by2 = (xyxy[idx, 3] - pad_y) / scale

            # Clip to image boundaries
            bx1 = max(0.0, min(float(bx1), float(orig_w)))
            by1 = max(0.0, min(float(by1), float(orig_h)))
            bx2 = max(0.0, min(float(bx2), float(orig_w)))
            by2 = max(0.0, min(float(by2), float(orig_h)))

            if bx2 <= bx1 or by2 <= by1:
                continue

            center_x = (bx1 + bx2) / 2.0
            center_y = (by1 + by2) / 2.0

            is_person = (cname == 'person')
            is_vehicle = (cname in {'car', 'motorcycle', 'bus', 'truck', 'bicycle'})

            detections.append({
                'box': [round(bx1, 1), round(by1, 1), round(bx2, 1), round(by2, 1)],
                'normalized_box': [
                    round(bx1 / orig_w, 4),
                    round(by1 / orig_h, 4),
                    round(bx2 / orig_w, 4),
                    round(by2 / orig_h, 4)
                ],
                'class_name': cname,
                'class_id': cid,
                'confidence': round(conf, 3),
                'center': (round(center_x, 1), round(center_y, 1)),
                'is_person': is_person,
                'is_vehicle': is_vehicle
            })

        # Person priority filter: Suppress spurious vehicle boxes overlapping with detected humans
        persons = [d for d in detections if d['is_person']]
        if persons:
            clean_dets = []
            for d in detections:
                if d['is_vehicle']:
                    from .tracker import calculate_iou
                    if any(calculate_iou(d['box'], p['box']) > 0.20 for p in persons):
                        continue
                clean_dets.append(d)
            detections = clean_dets

        return detections


# Global Singleton Getter
_detector_instance = None

def get_yolo_detector():
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = YOLODetector()
    return _detector_instance
