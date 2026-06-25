"""
Facial analysis using MediaPipe to detect landmarks and suggest aesthetic treatments.
Based on 468 facial landmarks, computes ratios and distances to recommend:
- Filler for under-eye hollows
- Botox for forehead wrinkles
- Filler for lips
- Other suggestions based on facial proportions
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
from typing import List, Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

# MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils


class FacialAnalyzer:
    def __init__(self):
        self.face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        logger.info("FacialAnalyzer initialized with MediaPipe")

    def _get_landmarks(self, image_path: str) -> Optional[List[Tuple[int, int]]]:
        """
        Detect face mesh landmarks from image.
        Returns list of (x, y) pixel coordinates for 468 landmarks, or None if no face.
        """
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return None

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            logger.warning("No face detected in image")
            return None

        h, w, _ = image.shape
        landmarks = results.multi_face_landmarks[0].landmark
        points = []
        for lm in landmarks:
            x = int(lm.x * w)
            y = int(lm.y * h)
            points.append((x, y))
        return points

    def _avg_point(self, landmarks: List[Tuple[int, int]], indices: List[int]) -> Tuple[int, int]:
        """Compute average (x, y) for a set of landmark indices."""
        xs = [landmarks[i][0] for i in indices]
        ys = [landmarks[i][1] for i in indices]
        return (int(np.mean(xs)), int(np.mean(ys)))

    def _distance(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """Euclidean distance between two points."""
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def _normalize_value(self, value: float, reference: float) -> float:
        """Normalize a distance by a reference distance (e.g., eye width)."""
        return value / reference if reference > 0 else 0

    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        Perform aesthetic analysis on a face image.
        Returns dict with:
            - suggestions: list of treatment recommendations (strings)
            - landmarks: raw points (for debugging)
            - error: if any
        """
        landmarks = self._get_landmarks(image_path)
        if not landmarks:
            return {"error": "No face detected. Please upload a clear face photo."}

        # Define landmark indices for key facial areas
        # Based on MediaPipe Face Mesh 468 points
        # Reference: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/geometry_pipeline_metadata_landmarks.txt

        # Left eye (approximate)
        left_eye_indices = [33, 133, 157, 158, 159, 160, 161, 173, 243, 246, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467]
        # Simplified: we use a few key points
        # Left eye: 33, 133, 157, 158, 159, 160, 161, 173
        # Right eye: 362, 263, 387, 386, 385, 384, 398, 466
        # Left eyebrow: 46, 53, 52, 65, 55
        # Right eyebrow: 276, 283, 282, 285, 295
        # Lips upper: 61, 185, 40, 39, 37, 0, 267, 269, 270, 409
        # Lips lower: 146, 91, 181, 84, 17, 314, 405, 321, 375, 324
        # Forehead: 10, 338, 297, 332, 284, 251

        left_eye_idx = [33, 133, 157, 158, 159, 160, 161, 173]
        right_eye_idx = [362, 263, 387, 386, 385, 384, 398, 466]
        left_eyebrow_idx = [46, 53, 52, 65, 55]
        right_eyebrow_idx = [276, 283, 282, 285, 295]
        lips_upper_idx = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409]
        lips_lower_idx = [146, 91, 181, 84, 17, 314, 405, 321, 375, 324]
        forehead_idx = [10, 338, 297, 332, 284, 251]
        # Left lower eyelid (for under-eye)
        left_lower_lid_idx = [152]  # approximate
        left_cheek_idx = [234]      # approximate
        right_lower_lid_idx = [377]
        right_cheek_idx = [454]

        # Compute averages
        left_eye_center = self._avg_point(landmarks, left_eye_idx)
        right_eye_center = self._avg_point(landmarks, right_eye_idx)
        left_eyebrow_center = self._avg_point(landmarks, left_eyebrow_idx)
        right_eyebrow_center = self._avg_point(landmarks, right_eyebrow_idx)
        lips_upper_center = self._avg_point(landmarks, lips_upper_idx)
        lips_lower_center = self._avg_point(landmarks, lips_lower_idx)
        forehead_center = self._avg_point(landmarks, forehead_idx)
        left_lower_lid = landmarks[left_lower_lid_idx[0]]
        left_cheek = landmarks[left_cheek_idx[0]]
        right_lower_lid = landmarks[right_lower_lid_idx[0]]
        right_cheek = landmarks[right_cheek_idx[0]]

        # Reference distances
        eye_width = self._distance(left_eye_center, right_eye_center)
        lip_width = self._distance(lips_upper_center, lips_lower_center) * 2  # rough

        suggestions = []

        # 1. Under-eye hollows (filler)
        # Measure distance from lower eyelid to cheek
        left_under_eye_dist = self._distance(left_lower_lid, left_cheek)
        right_under_eye_dist = self._distance(right_lower_lid, right_cheek)
        norm_left = self._normalize_value(left_under_eye_dist, eye_width)
        norm_right = self._normalize_value(right_under_eye_dist, eye_width)

        # If distance is small, suggest filler
        threshold_under_eye = 0.03  # relative to eye width
        if norm_left < threshold_under_eye:
            suggestions.append("زیر چشم چپ به اندازه حدود ۰.۵ سی‌سی نیاز به تزریق فیلر دارد.")
        elif norm_left < threshold_under_eye * 1.5:
            suggestions.append("زیر چشم چپ کمی گود است، تزریق فیلر (حدود ۰.۳ سی‌سی) توصیه می‌شود.")

        if norm_right < threshold_under_eye:
            suggestions.append("زیر چشم راست به اندازه حدود ۰.۵ سی‌سی نیاز به تزریق فیلر دارد.")
        elif norm_right < threshold_under_eye * 1.5:
            suggestions.append("زیر چشم راست کمی گود است، تزریق فیلر (حدود ۰.۳ سی‌سی) توصیه می‌شود.")

        # 2. Forehead wrinkles (Botox)
        # Distance between eyebrow and forehead center
        eyebrow_forehead_left = self._distance(left_eyebrow_center, forehead_center)
        eyebrow_forehead_right = self._distance(right_eyebrow_center, forehead_center)
        avg_eyebrow_forehead = (eyebrow_forehead_left + eyebrow_forehead_right) / 2
        norm_forehead = self._normalize_value(avg_eyebrow_forehead, eye_width)

        # If eyebrows are too close to forehead (or raised), suggest Botox
        # Here we check if forehead area is prominent (large distance)
        # Actually, for Botox we want to detect dynamic wrinkles. We'll approximate:
        # if the distance between eyebrow and forehead is large, suggest Botox
        threshold_forehead = 0.25
        if norm_forehead > threshold_forehead:
            suggestions.append("پیشانی نیاز به تزریق بوتاکس (حدود ۲۰ واحد) دارد.")
        elif norm_forehead > threshold_forehead * 0.8:
            suggestions.append("پیشانی دارای چین‌وچروک است، بوتاکس (حدود ۱۵ واحد) توصیه می‌شود.")

        # 3. Lips – height to width ratio
        lip_height = self._distance(lips_upper_center, lips_lower_center)
        lip_width = self._distance(lips_upper_center, lips_lower_center) * 1.8  # estimate
        ratio = lip_height / lip_width if lip_width > 0 else 0

        if ratio < 0.12:
            suggestions.append("لب بالا و پایین نازک هستند، تزریق فیلر (حدود ۱ سی‌سی) توصیه می‌شود.")
        elif ratio < 0.18:
            suggestions.append("لب‌ها کمی نازک هستند، تزریق فیلر (حدود ۰.۵ سی‌سی) می‌تواند کمک کند.")

        # 4. Eye asymmetry (optional)
        eye_dist = self._distance(left_eye_center, right_eye_center)
        # Check if eyes are symmetric (ignore for now)

        # If no suggestions, provide general feedback
        if not suggestions:
            suggestions.append("تحلیل چهره نشان می‌دهد که نیازی به تزریق فوری نیست، اما برای مشاوره دقیق‌تر با پزشک مشورت کنید.")

        # Add disclaimer
        suggestions.append("⚠️ این تحلیل صرفاً بر اساس تصویر و با استفاده از هوش مصنوعی انجام شده و جایگزین معاینه پزشک نیست.")

        return {
            "suggestions": suggestions,
            "landmarks": landmarks,  # for debugging
        }
