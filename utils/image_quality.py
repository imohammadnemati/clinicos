# utils/image_quality.py
import cv2
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

def check_image_quality(image_path: str) -> Tuple[bool, str]:
    """
    Check image quality for facial analysis.
    Returns (is_valid, reason).
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return False, "Unable to read image"
        
        # Check resolution (minimum 200x200)
        h, w = img.shape[:2]
        if h < 200 or w < 200:
            return False, "Image resolution too low. Minimum 200x200 pixels."
        
        # Check brightness
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        if brightness < 30:
            return False, "Image too dark. Please ensure good lighting."
        if brightness > 220:
            return False, "Image too bright. Please avoid overexposure."
        
        # Check blur (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 100:
            return False, "Image is too blurry. Please take a clear photo."
        
        # Check face presence using Haar cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) == 0:
            return False, "No face detected. Please make sure your face is clearly visible."
        if len(faces) > 1:
            return False, "Multiple faces detected. Please send only your face."
        
        # Check face size (should be at least 30% of image)
        x, y, fw, fh = faces[0]
        face_ratio = (fw * fh) / (w * h)
        if face_ratio < 0.1:
            return False, "Face is too small. Please take a closer photo."
        
        return True, "Image quality is acceptable."
    
    except Exception as e:
        logger.error(f"Quality check error: {e}")
        return False, f"Quality check failed: {str(e)}"
