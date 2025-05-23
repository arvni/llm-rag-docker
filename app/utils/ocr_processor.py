import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import logging
from typing import Optional, Tuple, Dict, Any
import io

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Advanced OCR processor with image preprocessing and optimization"""
    
    def __init__(self):
        # OCR configuration for different document types
        self.ocr_configs = {
            'default': r'--oem 3 --psm 6',
            'single_column': r'--oem 3 --psm 4',
            'single_line': r'--oem 3 --psm 7',
            'single_word': r'--oem 3 --psm 8',
            'table': r'--oem 3 --psm 6',
            'sparse': r'--oem 3 --psm 11'
        }
        
        # Language support
        self.languages = {
            'english': 'eng',
            'spanish': 'spa',
            'french': 'fra',
            'german': 'deu',
            'chinese': 'chi_sim',
            'arabic': 'ara'
        }
    
    def preprocess_image(self, image: np.ndarray, preprocessing_type: str = 'default') -> np.ndarray:
        """Apply preprocessing to improve OCR accuracy"""
        
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            if preprocessing_type == 'scanned_document':
                return self._preprocess_scanned_document(gray)
            elif preprocessing_type == 'photo_document':
                return self._preprocess_photo_document(gray)
            elif preprocessing_type == 'low_quality':
                return self._preprocess_low_quality(gray)
            elif preprocessing_type == 'handwritten':
                return self._preprocess_handwritten(gray)
            else:
                return self._preprocess_default(gray)
                
        except Exception as e:
            logger.error(f"Error in image preprocessing: {e}")
            return image
    
    def _preprocess_default(self, image: np.ndarray) -> np.ndarray:
        """Default preprocessing pipeline"""
        # Noise removal
        denoised = cv2.medianBlur(image, 3)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Binarization
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _preprocess_scanned_document(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing for scanned documents"""
        # Deskewing
        deskewed = self._deskew_image(image)
        
        # Noise removal
        kernel = np.ones((1,1), np.uint8)
        cleaned = cv2.morphologyEx(deskewed, cv2.MORPH_CLOSE, kernel)
        cleaned = cv2.medianBlur(cleaned, 3)
        
        # Binarization with adaptive threshold
        binary = cv2.adaptiveThreshold(cleaned, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        return binary
    
    def _preprocess_photo_document(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing for photos of documents"""
        # Perspective correction (simplified)
        corrected = self._correct_perspective(image)
        
        # Shadow removal
        shadow_free = self._remove_shadows(corrected)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(shadow_free)
        
        # Sharpening
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Binarization
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _preprocess_low_quality(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing for low quality images"""
        # Upscaling
        upscaled = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Heavy denoising
        denoised = cv2.fastNlMeansDenoising(upscaled, None, 10, 7, 21)
        
        # Sharpening
        kernel = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])
        sharpened = cv2.filter2D(denoised, -1, kernel)
        
        # Contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
        enhanced = clahe.apply(sharpened)
        
        # Binarization
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _preprocess_handwritten(self, image: np.ndarray) -> np.ndarray:
        """Preprocessing for handwritten text"""
        # Gentle denoising
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        
        # Morphological operations to connect broken characters
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        morphed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
        
        # Adaptive binarization
        binary = cv2.adaptiveThreshold(morphed, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 15, 10)
        
        return binary
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Correct skew in scanned documents"""
        # Find text lines using Hough transform
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # Calculate average angle
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = theta * 180 / np.pi - 90
                if abs(angle) < 45:  # Only consider reasonable angles
                    angles.append(angle)
            
            if angles:
                avg_angle = np.median(angles)
                
                # Rotate image
                h, w = image.shape
                center = (w // 2, h // 2)
                rotation_matrix = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
                rotated = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                       flags=cv2.INTER_CUBIC, 
                                       borderMode=cv2.BORDER_REPLICATE)
                return rotated
        
        return image
    
    def _correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """Simple perspective correction"""
        # This is a simplified version - in practice, you'd need edge detection
        # and corner finding for full perspective correction
        return image
    
    def _remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """Remove shadows from document images"""
        # Dilate the image to create a mask
        dilated_img = cv2.dilate(image, np.ones((7,7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        
        # Calculate the difference
        diff_img = 255 - cv2.absdiff(image, bg_img)
        
        # Normalize
        norm_img = cv2.normalize(diff_img, None, alpha=0, beta=255, 
                               norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        
        return norm_img
    
    def extract_text(self, image: Image.Image, 
                    config_type: str = 'default',
                    language: str = 'english',
                    preprocessing: str = 'default',
                    confidence_threshold: float = 0.0) -> Dict[str, Any]:
        """Extract text from image with OCR"""
        
        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Preprocess image
            processed_img = self.preprocess_image(img_array, preprocessing)
            
            # Convert back to PIL
            processed_pil = Image.fromarray(processed_img)
            
            # Get OCR configuration
            config = self.ocr_configs.get(config_type, self.ocr_configs['default'])
            lang = self.languages.get(language, 'eng')
            
            # Extract text with confidence scores
            data = pytesseract.image_to_data(processed_pil, 
                                           config=config,
                                           lang=lang,
                                           output_type=pytesseract.Output.DICT)
            
            # Filter by confidence
            text_parts = []
            confidences = []
            
            for i, conf in enumerate(data['conf']):
                if int(conf) > confidence_threshold:
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(conf))
            
            full_text = ' '.join(text_parts)
            avg_confidence = np.mean(confidences) if confidences else 0
            
            return {
                'text': full_text,
                'confidence': avg_confidence,
                'word_confidences': confidences,
                'preprocessing_used': preprocessing,
                'config_used': config_type,
                'language_used': language
            }
            
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {
                'text': '',
                'confidence': 0,
                'error': str(e)
            }
    
    def detect_language(self, image: Image.Image) -> str:
        """Detect the language of text in image"""
        try:
            # Try OCR with language detection
            osd = pytesseract.image_to_osd(image)
            
            # Parse orientation and script detection output
            lines = osd.split('\n')
            for line in lines:
                if 'Script:' in line:
                    script = line.split(':')[1].strip()
                    # Map script to language (simplified)
                    script_to_lang = {
                        'Latin': 'english',
                        'Arabic': 'arabic',
                        'Han': 'chinese'
                    }
                    return script_to_lang.get(script, 'english')
            
            return 'english'  # Default
            
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return 'english'
    
    def get_text_regions(self, image: Image.Image) -> List[Dict]:
        """Detect text regions in image"""
        try:
            # Get bounding boxes for text regions
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            regions = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Confidence threshold
                    text = data['text'][i].strip()
                    if text:
                        regions.append({
                            'text': text,
                            'confidence': int(data['conf'][i]),
                            'bbox': {
                                'x': data['left'][i],
                                'y': data['top'][i],
                                'width': data['width'][i],
                                'height': data['height'][i]
                            }
                        })
            
            return regions
            
        except Exception as e:
            logger.error(f"Text region detection error: {e}")
            return []