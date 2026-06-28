# utils/facial_metrics.py
import numpy as np
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

def compute_facial_metrics(landmarks: List[Tuple[int, int]]) -> Dict[str, float]:
    """Compute aesthetic metrics from 468 facial landmarks."""
    if not landmarks or len(landmarks) < 468:
        return {}
    
    # Helper functions
    def distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))
    
    def angle(p1, p2, p3):
        v1 = np.array(p1) - np.array(p2)
        v2 = np.array(p3) - np.array(p2)
        cos = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
        return np.arccos(np.clip(cos, -1.0, 1.0)) * 180 / np.pi
    
    # Define key landmark indices (based on MediaPipe 468)
    left_eye_idx = [33, 133, 157, 158, 159, 160, 161, 173]
    right_eye_idx = [362, 263, 387, 386, 385, 384, 398, 466]
    left_eyebrow_idx = [46, 53, 52, 65, 55]
    right_eyebrow_idx = [276, 283, 282, 285, 295]
    lips_upper = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409]
    lips_lower = [146, 91, 181, 84, 17, 314, 405, 321, 375, 324]
    nose_tip = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467]
    # For simplicity, we use known indices from MediaPipe documentation
    
    # Extract specific points
    left_eye_center = np.mean([landmarks[i] for i in left_eye_idx], axis=0)
    right_eye_center = np.mean([landmarks[i] for i in right_eye_idx], axis=0)
    left_eyebrow_center = np.mean([landmarks[i] for i in left_eyebrow_idx], axis=0)
    right_eyebrow_center = np.mean([landmarks[i] for i in right_eyebrow_idx], axis=0)
    lips_upper_center = np.mean([landmarks[i] for i in lips_upper], axis=0)
    lips_lower_center = np.mean([landmarks[i] for i in lips_lower], axis=0)
    nose_tip_point = landmarks[1]  # index 1 is nose tip
    
    # Compute distances
    eye_width = distance(left_eye_center, right_eye_center)
    lip_height = distance(lips_upper_center, lips_lower_center)
    lip_width = distance(landmarks[61], landmarks[291])  # corners of mouth
    nose_width = distance(landmarks[49], landmarks[279])  # nostrils
    jaw_width = distance(landmarks[356], landmarks[10])  # jaw points
    
    # Symmetry: compare left and right sides
    left_eye_eyebrow_dist = distance(left_eye_center, left_eyebrow_center)
    right_eye_eyebrow_dist = distance(right_eye_center, right_eyebrow_center)
    eye_symmetry = 1 - abs(left_eye_eyebrow_dist - right_eye_eyebrow_dist) / (left_eye_eyebrow_dist + right_eye_eyebrow_dist + 1e-8)
    
    # Skin quality proxy: using texture analysis would require more complex processing,
    # here we use a placeholder based on lip and eye features
    skin_quality = 0.7 + 0.3 * (1 - (lip_width / (eye_width + 1e-8)) * 0.5)
    
    # Youthfulness: based on eye-to-eyebrow distance (higher = more youthful)
    youthfulness = min(1.0, (left_eye_eyebrow_dist + right_eye_eyebrow_dist) / (eye_width + 1e-8))
    
    # Volume balance: ratio of cheek to jaw
    cheek_volume = distance(landmarks[234], landmarks[454])  # cheek points
    volume_balance = cheek_volume / (jaw_width + 1e-8)
    
    # Facial harmony: combination of symmetry, proportions
    harmony = (eye_symmetry + youthfulness + volume_balance) / 3
    
    # Overall beauty score (weighted combination)
    overall = (eye_symmetry * 0.3 + skin_quality * 0.25 + youthfulness * 0.2 + volume_balance * 0.15 + harmony * 0.1) * 100
    
    return {
        'eye_symmetry': eye_symmetry * 100,
        'skin_quality': skin_quality * 100,
        'youthfulness': youthfulness * 100,
        'volume_balance': volume_balance * 100,
        'facial_harmony': harmony * 100,
        'overall_beauty': overall,
        'lip_to_eye_ratio': lip_height / (eye_width + 1e-8),
        'nose_to_lip_ratio': distance(nose_tip_point, lips_upper_center) / (eye_width + 1e-8),
    }
