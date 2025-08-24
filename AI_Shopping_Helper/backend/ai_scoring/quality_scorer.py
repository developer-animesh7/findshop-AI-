"""
AI Quality Scoring System for products
Based on the document specifications for calculating quality scores
"""

import json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class QualityScorer:
    """Calculates quality scores for products based on category-specific metrics"""
    
    def __init__(self):
        # Category scorecards with weighted features
        self.category_scorecards = {
            'headphones': {
                'battery_life': 30,  # max points for battery life
                'driver_size': 25,   # max points for driver size
                'noise_cancellation': 20,  # max points for noise cancellation
                'build_quality': 15,  # max points for build quality
                'frequency_response': 10   # max points for frequency response
            },
            'trimmer': {
                'runtime': 30,       # max points for runtime
                'blade_material': 25, # max points for blade material
                'waterproof': 20,    # max points for waterproof rating
                'attachments': 15,   # max points for attachments
                'charging_time': 10  # max points for charging time
            },
            'mixer': {
                'power_output': 30,  # max points for power (watts)
                'jar_count': 25,     # max points for number of jars
                'speed_settings': 20, # max points for speed settings
                'warranty': 15,      # max points for warranty period
                'safety_features': 10 # max points for safety features
            },
            'smartphone': {
                'camera': 25,        # max points for camera specs
                'battery': 25,       # max points for battery capacity
                'processor': 20,     # max points for processor
                'ram': 15,          # max points for RAM
                'storage': 15       # max points for storage
            },
            'laptop': {
                'processor': 30,     # max points for processor
                'ram': 25,          # max points for RAM
                'storage': 20,      # max points for storage
                'display': 15,      # max points for display
                'battery': 10       # max points for battery
            },
            'clothing': {
                'material': 30,      # max points for material quality
                'fit': 25,          # max points for fit
                'durability': 20,   # max points for durability
                'comfort': 15,      # max points for comfort
                'design': 10        # max points for design
            },
            'general': {
                'quality': 40,       # max points for general quality
                'features': 30,      # max points for features
                'durability': 20,    # max points for durability
                'value': 10          # max points for value
            }
        }
        
        # Reference values for normalization
        self.reference_values = {
            'headphones': {
                'battery_life': 40,      # hours
                'driver_size': 50,       # mm
                'noise_cancellation': 1, # boolean (0 or 1)
                'build_quality': 5,      # scale 1-5
                'frequency_response': 40000  # Hz
            },
            'trimmer': {
                'runtime': 120,          # minutes
                'blade_material': 5,     # scale 1-5 (stainless steel = 5)
                'waterproof': 1,         # boolean
                'attachments': 10,       # number of attachments
                'charging_time': 8       # hours (lower is better, inverted)
            },
            'mixer': {
                'power_output': 1000,    # watts
                'jar_count': 5,          # number of jars
                'speed_settings': 10,    # number of speed settings
                'warranty': 5,           # years
                'safety_features': 5     # scale 1-5
            },
            'smartphone': {
                'camera': 108,           # MP
                'battery': 5000,         # mAh
                'processor': 5,          # scale 1-5
                'ram': 12,              # GB
                'storage': 256          # GB
            }
        }
    
    def calculate_quality_score(self, product_specs: Dict, category: str) -> float:
        """
        Calculate quality score based on product specifications and category
        
        Args:
            product_specs (dict): Product specifications
            category (str): Product category
            
        Returns:
            float: Quality score (0-100)
        """
        try:
            if category not in self.category_scorecards:
                category = 'general'
            
            scorecard = self.category_scorecards[category]
            reference_vals = self.reference_values.get(category, {})
            
            total_points = 0
            max_possible_points = sum(scorecard.values())
            
            # Extract and normalize specs for scoring
            normalized_specs = self._normalize_specs(product_specs, category)
            
            for feature, max_points in scorecard.items():
                if feature in normalized_specs:
                    value = normalized_specs[feature]
                    reference_val = reference_vals.get(feature, 1)
                    
                    # Calculate points for this feature
                    if feature == 'charging_time':  # Lower is better for charging time
                        points = max_points * (1 - min(value / reference_val, 1))
                    else:  # Higher is better for most features
                        points = max_points * min(value / reference_val, 1)
                    
                    total_points += points
                else:
                    # Use default value if spec is missing (60% of max points)
                    total_points += max_points * 0.6
            
            # Convert to 0-100 scale
            quality_score = (total_points / max_possible_points) * 100
            
            # Ensure score is within bounds
            return max(0, min(100, quality_score))
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {str(e)}")
            return 60.0  # Default score
    
    def calculate_final_score(self, quality_score: float, rating: float) -> float:
        """
        Calculate final score incorporating user ratings
        
        Args:
            quality_score (float): Quality score (0-100)
            rating (float): User rating (1-5)
            
        Returns:
            float: Final score
        """
        try:
            # Normalize rating to 0-1 scale
            normalized_rating = rating / 5.0
            
            # Final score = Quality Score × Rating
            final_score = quality_score * normalized_rating
            
            return round(final_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating final score: {str(e)}")
            return quality_score * 0.8  # Default to 80% of quality score
    
    def _normalize_specs(self, product_specs: Dict, category: str) -> Dict:
        """
        Normalize product specifications for scoring
        
        Args:
            product_specs (dict): Raw product specifications
            category (str): Product category
            
        Returns:
            dict: Normalized specifications
        """
        normalized = {}
        
        try:
            if category == 'headphones':
                normalized.update(self._normalize_headphones_specs(product_specs))
            elif category == 'trimmer':
                normalized.update(self._normalize_trimmer_specs(product_specs))
            elif category == 'mixer':
                normalized.update(self._normalize_mixer_specs(product_specs))
            elif category == 'smartphone':
                normalized.update(self._normalize_smartphone_specs(product_specs))
            elif category == 'laptop':
                normalized.update(self._normalize_laptop_specs(product_specs))
            elif category == 'clothing':
                normalized.update(self._normalize_clothing_specs(product_specs))
            else:
                normalized.update(self._normalize_general_specs(product_specs))
                
        except Exception as e:
            logger.error(f"Error normalizing specs for {category}: {str(e)}")
        
        return normalized
    
    def _normalize_headphones_specs(self, specs: Dict) -> Dict:
        """Normalize headphones specifications"""
        normalized = {}
        
        # Battery life (extract hours)
        if 'battery_life' in specs or 'Battery Life' in specs:
            battery_text = specs.get('battery_life', specs.get('Battery Life', ''))
            battery_hours = self._extract_numeric_value(battery_text, patterns=[r'(\d+)\s*h'])
            if battery_hours:
                normalized['battery_life'] = battery_hours
        
        # Driver size (extract mm)
        if 'driver_size' in specs or 'Driver Size' in specs:
            driver_text = specs.get('driver_size', specs.get('Driver Size', ''))
            driver_size = self._extract_numeric_value(driver_text, patterns=[r'(\d+)\s*mm'])
            if driver_size:
                normalized['driver_size'] = driver_size
        
        # Noise cancellation (boolean)
        noise_keywords = ['noise cancellation', 'anc', 'active noise']
        specs_text = ' '.join(str(v).lower() for v in specs.values())
        if any(keyword in specs_text for keyword in noise_keywords):
            normalized['noise_cancellation'] = 1
        else:
            normalized['noise_cancellation'] = 0
        
        # Build quality (extract from materials or infer from price range)
        build_quality = 3  # Default mid-range
        materials = ['metal', 'aluminum', 'premium', 'steel']
        if any(material in specs_text for material in materials):
            build_quality = 5
        elif any(word in specs_text for word in ['plastic', 'basic']):
            build_quality = 2
        normalized['build_quality'] = build_quality
        
        # Frequency response (extract Hz)
        freq_text = specs.get('frequency_response', specs.get('Frequency Response', ''))
        freq_value = self._extract_numeric_value(freq_text, patterns=[r'(\d+)\s*hz', r'(\d+)\s*khz'])
        if freq_value:
            normalized['frequency_response'] = freq_value
        
        return normalized
    
    def _normalize_trimmer_specs(self, specs: Dict) -> Dict:
        """Normalize trimmer specifications"""
        normalized = {}
        
        # Runtime (extract minutes)
        runtime_text = specs.get('runtime', specs.get('Battery Life', ''))
        runtime_minutes = self._extract_numeric_value(runtime_text, patterns=[r'(\d+)\s*min'])
        if runtime_minutes:
            normalized['runtime'] = runtime_minutes
        
        # Blade material
        blade_quality = 3  # Default
        specs_text = ' '.join(str(v).lower() for v in specs.values())
        if 'stainless steel' in specs_text or 'titanium' in specs_text:
            blade_quality = 5
        elif 'steel' in specs_text:
            blade_quality = 4
        elif 'ceramic' in specs_text:
            blade_quality = 4
        normalized['blade_material'] = blade_quality
        
        # Waterproof
        if any(word in specs_text for word in ['waterproof', 'water resistant', 'ipx']):
            normalized['waterproof'] = 1
        else:
            normalized['waterproof'] = 0
        
        # Attachments (count)
        attachments_text = specs.get('attachments', specs.get('Accessories', ''))
        attachments_count = self._extract_numeric_value(attachments_text, patterns=[r'(\d+)'])
        if attachments_count:
            normalized['attachments'] = attachments_count
        
        return normalized
    
    def _normalize_mixer_specs(self, specs: Dict) -> Dict:
        """Normalize mixer specifications"""
        normalized = {}
        
        # Power output (watts)
        power_text = specs.get('power', specs.get('Power', ''))
        power_watts = self._extract_numeric_value(power_text, patterns=[r'(\d+)\s*w'])
        if power_watts:
            normalized['power_output'] = power_watts
        
        # Jar count
        jar_text = specs.get('jars', specs.get('Jars', ''))
        jar_count = self._extract_numeric_value(jar_text, patterns=[r'(\d+)'])
        if jar_count:
            normalized['jar_count'] = jar_count
        
        # Speed settings
        speed_text = specs.get('speeds', specs.get('Speed Settings', ''))
        speed_count = self._extract_numeric_value(speed_text, patterns=[r'(\d+)'])
        if speed_count:
            normalized['speed_settings'] = speed_count
        
        return normalized
    
    def _normalize_smartphone_specs(self, specs: Dict) -> Dict:
        """Normalize smartphone specifications"""
        normalized = {}
        
        # Camera (extract MP)
        camera_text = specs.get('camera', specs.get('Camera', ''))
        camera_mp = self._extract_numeric_value(camera_text, patterns=[r'(\d+)\s*mp'])
        if camera_mp:
            normalized['camera'] = camera_mp
        
        # Battery (extract mAh)
        battery_text = specs.get('battery', specs.get('Battery', ''))
        battery_mah = self._extract_numeric_value(battery_text, patterns=[r'(\d+)\s*mah'])
        if battery_mah:
            normalized['battery'] = battery_mah
        
        # RAM (extract GB)
        ram_text = specs.get('ram', specs.get('RAM', ''))
        ram_gb = self._extract_numeric_value(ram_text, patterns=[r'(\d+)\s*gb'])
        if ram_gb:
            normalized['ram'] = ram_gb
        
        return normalized
    
    def _normalize_laptop_specs(self, specs: Dict) -> Dict:
        """Normalize laptop specifications"""
        normalized = {}
        
        # Similar to smartphone but with different focus
        # This can be expanded based on specific requirements
        
        return normalized
    
    def _normalize_clothing_specs(self, specs: Dict) -> Dict:
        """Normalize clothing specifications"""
        normalized = {}
        
        # Material quality
        specs_text = ' '.join(str(v).lower() for v in specs.values())
        material_quality = 3  # Default
        
        premium_materials = ['cotton', 'silk', 'wool', 'linen', 'organic']
        basic_materials = ['polyester', 'synthetic', 'blend']
        
        if any(material in specs_text for material in premium_materials):
            material_quality = 5
        elif any(material in specs_text for material in basic_materials):
            material_quality = 2
        
        normalized['material'] = material_quality
        
        return normalized
    
    def _normalize_general_specs(self, specs: Dict) -> Dict:
        """Normalize general product specifications"""
        normalized = {}
        
        # General quality assessment based on available specs
        normalized['quality'] = 3  # Default mid-range
        normalized['features'] = len(specs)  # Number of features
        normalized['durability'] = 3  # Default
        normalized['value'] = 3  # Default
        
        return normalized
    
    def _extract_numeric_value(self, text: str, patterns: List[str]) -> float:
        """
        Extract numeric value from text using regex patterns
        
        Args:
            text (str): Text to extract from
            patterns (list): List of regex patterns to try
            
        Returns:
            float: Extracted numeric value or None
        """
        import re
        
        if not text:
            return None
        
        text = str(text).lower()
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # Handle kHz to Hz conversion
                    if 'khz' in text:
                        value *= 1000
                    return value
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def get_category_scorecard(self, category: str) -> Dict:
        """Get scorecard for a specific category"""
        return self.category_scorecards.get(category, self.category_scorecards['general'])
    
    def add_custom_scorecard(self, category: str, scorecard: Dict):
        """Add a custom scorecard for a new category"""
        self.category_scorecards[category] = scorecard
        logger.info(f"Added custom scorecard for category: {category}")
