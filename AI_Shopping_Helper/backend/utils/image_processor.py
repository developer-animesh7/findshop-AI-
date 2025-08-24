"""
Image processing utilities for product analysis
"""

import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
import base64
import io
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Processes product images to extract information"""
    
    def __init__(self):
        # Configure Tesseract (adjust path as needed)
        # pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'
        pass
    
    def extract_product_info(self, image_data: str) -> Optional[Dict]:
        """
        Extract product information from image
        
        Args:
            image_data (str): Base64 encoded image data or image URL
            
        Returns:
            dict: Extracted product information
        """
        try:
            # Convert image data to PIL Image
            image = self._load_image(image_data)
            if image is None:
                return None
            
            # Convert to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Try to extract text from image
            extracted_text = self._extract_text_from_image(cv_image)
            
            if not extracted_text:
                # If no text found, try to identify product type from image
                return self._identify_product_from_image(cv_image)
            
            # Parse extracted text for product information
            product_info = self._parse_product_text(extracted_text)
            
            return product_info
            
        except Exception as e:
            logger.error(f"Error extracting product info from image: {str(e)}")
            return None
    
    def _load_image(self, image_data: str) -> Optional[Image.Image]:
        """Load image from base64 string or URL"""
        try:
            if image_data.startswith('data:image'):
                # Base64 encoded image
                header, data = image_data.split(',', 1)
                image_bytes = base64.b64decode(data)
                return Image.open(io.BytesIO(image_bytes))
            
            elif image_data.startswith('http'):
                # URL - would need requests to download
                # For now, return None
                logger.warning("URL image loading not implemented yet")
                return None
            
            else:
                # Assume it's a file path
                return Image.open(image_data)
                
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return None
    
    def _extract_text_from_image(self, cv_image) -> str:
        """Extract text from image using OCR"""
        try:
            # Preprocessing for better OCR
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get black and white image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Remove noise
            kernel = np.ones((1, 1), np.uint8)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
            
            # Extract text using Tesseract
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(thresh, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            return ""
    
    def _parse_product_text(self, text: str) -> Dict:
        """Parse extracted text to identify product information"""
        try:
            product_info = {
                'name': '',
                'price': 0,
                'specs': {},
                'category': 'general',
                'rating': 4.0
            }
            
            lines = text.split('\\n')
            text_lower = text.lower()
            
            # Extract price
            price_patterns = [
                r'₹[\s]*([0-9,]+)',
                r'rs\.?[\s]*([0-9,]+)',
                r'inr[\s]*([0-9,]+)',
                r'price[\s]*:?[\s]*₹?[\s]*([0-9,]+)'
            ]
            
            for pattern in price_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    price_str = match.group(1).replace(',', '')
                    try:
                        product_info['price'] = int(price_str)
                        break
                    except ValueError:
                        continue
            
            # Extract specifications
            spec_patterns = {
                'battery': r'battery[\s]*:?[\s]*([^\\n]+)',
                'battery_life': r'battery life[\s]*:?[\s]*([^\\n]+)',
                'runtime': r'runtime[\s]*:?[\s]*([^\\n]+)',
                'power': r'power[\s]*:?[\s]*([^\\n]+)',
                'ram': r'ram[\s]*:?[\s]*([^\\n]+)',
                'storage': r'storage[\s]*:?[\s]*([^\\n]+)',
                'camera': r'camera[\s]*:?[\s]*([^\\n]+)',
                'display': r'display[\s]*:?[\s]*([^\\n]+)',
                'processor': r'processor[\s]*:?[\s]*([^\\n]+)'
            }
            
            for spec_name, pattern in spec_patterns.items():
                match = re.search(pattern, text_lower)
                if match:
                    product_info['specs'][spec_name] = match.group(1).strip()
            
            # Extract rating
            rating_patterns = [
                r'(\d+\.?\d*)\s*/\s*5',
                r'rating[\s]*:?[\s]*(\d+\.?\d*)',
                r'(\d+\.?\d*)\s*stars?'
            ]
            
            for pattern in rating_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    try:
                        product_info['rating'] = float(match.group(1))
                        break
                    except ValueError:
                        continue
            
            # Determine category based on text content
            product_info['category'] = self._determine_category_from_text(text_lower)
            
            # Extract product name (usually the first meaningful line)
            for line in lines:
                line = line.strip()
                if len(line) > 5 and not any(char in line for char in ['₹', 'Rs', 'Price', ':']):
                    product_info['name'] = line
                    break
            
            return product_info
            
        except Exception as e:
            logger.error(f"Error parsing product text: {str(e)}")
            return {}
    
    def _identify_product_from_image(self, cv_image) -> Dict:
        """Identify product type from image using computer vision"""
        try:
            # This is a simplified version - in production, you'd use ML models
            # For now, return a generic product structure
            return {
                'name': 'Product from Image',
                'price': 0,
                'specs': {},
                'category': 'general',
                'rating': 4.0,
                'source': 'image_analysis'
            }
            
        except Exception as e:
            logger.error(f"Error identifying product from image: {str(e)}")
            return {}
    
    def _determine_category_from_text(self, text: str) -> str:
        """Determine product category from text content"""
        categories = {
            'headphones': ['headphone', 'earphone', 'earbud', 'audio', 'sound', 'music'],
            'smartphone': ['phone', 'mobile', 'smartphone', 'android', 'ios', 'iphone'],
            'laptop': ['laptop', 'notebook', 'computer', 'pc', 'macbook'],
            'trimmer': ['trimmer', 'shaver', 'grooming', 'beard', 'hair'],
            'mixer': ['mixer', 'grinder', 'blender', 'kitchen', 'juicer'],
            'charger': ['charger', 'adapter', 'cable', 'charging'],
            'clothing': ['shirt', 'pant', 'dress', 'jacket', 'wear', 'cotton', 'fabric'],
            'shoes': ['shoe', 'sneaker', 'boot', 'sandal', 'footwear']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general'
    
    def enhance_image_for_ocr(self, image_path: str) -> str:
        """Enhance image quality for better OCR results"""
        try:
            # Read image
            image = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Save processed image
            output_path = image_path.replace('.', '_processed.')
            cv2.imwrite(output_path, processed)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error enhancing image: {str(e)}")
            return image_path
    
    def detect_highlighted_areas(self, cv_image) -> List[Dict]:
        """Detect highlighted or marked areas in image"""
        try:
            # Convert to HSV for better color detection
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # Define range for common highlight colors (yellow, green, red)
            highlight_ranges = [
                # Yellow highlights
                (np.array([20, 100, 100]), np.array([30, 255, 255])),
                # Green highlights  
                (np.array([40, 50, 50]), np.array([80, 255, 255])),
                # Red highlights
                (np.array([0, 120, 70]), np.array([10, 255, 255]))
            ]
            
            highlighted_areas = []
            
            for i, (lower, upper) in enumerate(highlight_ranges):
                # Create mask
                mask = cv2.inRange(hsv, lower, upper)
                
                # Find contours
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 500:  # Filter small areas
                        x, y, w, h = cv2.boundingRect(contour)
                        highlighted_areas.append({
                            'x': x, 'y': y, 'width': w, 'height': h,
                            'area': area, 'color_type': i
                        })
            
            return highlighted_areas
            
        except Exception as e:
            logger.error(f"Error detecting highlighted areas: {str(e)}")
            return []
    
    def extract_text_from_region(self, cv_image, x: int, y: int, w: int, h: int) -> str:
        """Extract text from a specific region of the image"""
        try:
            # Crop the region
            roi = cv_image[y:y+h, x:x+w]
            
            # Convert to grayscale
            gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh_roi = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text
            text = pytesseract.image_to_string(thresh_roi, config='--psm 7')
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from region: {str(e)}")
            return ""
