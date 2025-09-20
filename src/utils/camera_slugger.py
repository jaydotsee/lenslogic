"""
Camera name slugification utilities for professional photo organization
"""

import re
from typing import Dict, Optional


class CameraSlugger:
    """Converts camera names to clean, consistent slugs for file organization"""

    def __init__(self, custom_mappings: Optional[Dict[str, str]] = None):
        """
        Initialize with optional custom mappings

        Args:
            custom_mappings: Dict mapping full camera names to preferred slugs
        """
        self.custom_mappings = custom_mappings or {}

        # Built-in mappings for common camera patterns
        self.built_in_mappings = {
            # iPhone models
            r'iPhone\s+(\d+)\s+Pro\s+Max': r'iphone\1promax',
            r'iPhone\s+(\d+)\s+Pro': r'iphone\1pro',
            r'iPhone\s+(\d+)\s+Plus': r'iphone\1plus',
            r'iPhone\s+(\d+)\s+mini': r'iphone\1mini',
            r'iPhone\s+(\d+)': r'iphone\1',
            r'iPhone\s+SE\s+\((\d+)\w+\s+generation\)': r'iphonese\1',
            r'iPhone\s+SE': r'iphonese',
            r'iPhone\s+XS\s+Max': r'iphonexsmax',
            r'iPhone\s+XS': r'iphonexs',
            r'iPhone\s+XR': r'iphonexr',
            r'iPhone\s+X': r'iphonex',

            # Canon models
            r'Canon\s+EOS\s+(\w+)': r'canon\1',
            r'Canon\s+PowerShot\s+(\w+)': r'canpwr\1',
            r'Canon\s+EOS\s+R(\d+)': r'canonr\1',
            r'Canon\s+EOS\s+(\d+)D': r'canon\1d',

            # Nikon models
            r'Nikon\s+D(\d+)': r'nikond\1',
            r'Nikon\s+Z\s?(\d+)': r'nikonz\1',
            r'Nikon\s+COOLPIX\s+(\w+)': r'nikcpx\1',

            # Sony models
            r'Sony\s+ILCE-(\d+\w*)': r'sonya\1',  # Alpha series
            r'Sony\s+DSC-(\w+)': r'sonydsc\1',
            r'Sony\s+Alpha\s+(\w+)': r'sonya\1',
            r'Sony\s+FX(\d+)': r'sonyfx\1',

            # Fujifilm models
            r'Fujifilm\s+X-(\w+)': r'fujix\1',
            r'Fujifilm\s+FinePix\s+(\w+)': r'fujifp\1',
            r'Fujifilm\s+GFX\s?(\d+\w*)': r'fujigfx\1',

            # Panasonic models
            r'Panasonic\s+DMC-(\w+)': r'pandmc\1',
            r'Panasonic\s+DC-(\w+)': r'pandc\1',
            r'Panasonic\s+LUMIX\s+(\w+)': r'panlx\1',

            # GoPro models
            r'GoPro\s+HERO(\d+)': r'gopro\1',
            r'GoPro\s+(\w+)': r'gopro\1',

            # DJI models
            r'DJI\s+(\w+)': r'dji\1',

            # Generic smartphone patterns
            r'Samsung\s+Galaxy\s+(\w+)': r'galaxy\1',
            r'Google\s+Pixel\s+(\d+\w*)': r'pixel\1',
            r'OnePlus\s+(\d+\w*)': r'oneplus\1',
            r'Xiaomi\s+(\w+)': r'xiaomi\1',

            # Action cameras
            r'Insta360\s+(\w+)': r'insta\1',
            r'Garmin\s+VIRB\s+(\w+)': r'garmin\1',
        }

    def create_slug(self, camera_make: str = '', camera_model: str = '') -> str:
        """
        Create a clean slug from camera make and model

        Args:
            camera_make: Camera manufacturer
            camera_model: Camera model name

        Returns:
            Clean slug suitable for file naming
        """
        # Combine make and model for pattern matching
        full_name = f"{camera_make} {camera_model}".strip()

        if not full_name:
            return 'unknown'

        # Check custom mappings first (exact match only)
        for pattern, replacement in self.custom_mappings.items():
            if pattern.lower() == full_name.lower():
                return self._clean_slug(replacement)

        # Check built-in pattern mappings
        for pattern, replacement in self.built_in_mappings.items():
            match = re.search(pattern, full_name, re.IGNORECASE)
            if match:
                # Replace capture groups in the replacement string
                result = replacement
                for i, group in enumerate(match.groups(), 1):
                    result = result.replace(f'\\{i}', group.lower())
                return self._clean_slug(result)

        # Fallback: create slug from model name
        return self._create_fallback_slug(camera_model or camera_make)

    def _create_fallback_slug(self, name: str) -> str:
        """Create a fallback slug when no patterns match"""
        if not name:
            return 'unknown'

        # Remove manufacturer prefix if present
        name = re.sub(r'^(canon|nikon|sony|fujifilm|panasonic|olympus|pentax|leica|samsung|apple|google|oneplus|xiaomi|huawei|oppo|vivo|realme|motorola|lg|htc|nokia|blackberry)\s+', '', name, flags=re.IGNORECASE)

        # Basic cleanup
        slug = name.lower()
        slug = re.sub(r'[^\w\d\-]', '', slug)  # Remove special chars except hyphens
        slug = re.sub(r'\-+', '-', slug)  # Collapse multiple hyphens
        slug = slug.strip('-')  # Remove leading/trailing hyphens

        # Truncate if too long
        if len(slug) > 15:
            slug = slug[:15].rstrip('-')

        return slug or 'unknown'

    def _clean_slug(self, slug: str) -> str:
        """Clean and validate a slug"""
        if not slug:
            return 'unknown'

        # Ensure lowercase and clean
        slug = slug.lower()
        slug = re.sub(r'[^\w\d\-]', '', slug)
        slug = re.sub(r'\-+', '-', slug)
        slug = slug.strip('-')

        return slug or 'unknown'

    def get_examples(self) -> Dict[str, str]:
        """Get examples of camera name to slug conversions"""
        examples = {
            # iPhone examples
            'Apple iPhone 15 Pro Max': 'iphone15promax',
            'Apple iPhone 14 Pro': 'iphone14pro',
            'Apple iPhone 13 mini': 'iphone13mini',
            'Apple iPhone 12': 'iphone12',
            'Apple iPhone SE (3rd generation)': 'iphonese3',
            'Apple iPhone X': 'iphonex',

            # DSLR examples
            'Canon EOS R5': 'canonr5',
            'Canon EOS 5D Mark IV': 'canon5d',
            'Nikon D850': 'nikond850',
            'Nikon Z9': 'nikonz9',
            'Sony ILCE-7RM5': 'sonya7rm5',
            'Sony Alpha 7 IV': 'sonya7iv',

            # Mirrorless examples
            'Fujifilm X-T5': 'fujixt5',
            'Fujifilm GFX100S': 'fujigfx100s',
            'Panasonic LUMIX DC-GH6': 'pandc-gh6',

            # Action cameras
            'GoPro HERO12': 'gopro12',
            'DJI Action 2': 'djiaction2',
            'Insta360 X3': 'instax3',

            # Smartphones
            'Samsung Galaxy S24 Ultra': 'galaxys24ultra',
            'Google Pixel 8 Pro': 'pixel8pro',
            'OnePlus 12': 'oneplus12',
        }

        # Process examples through the actual slug creation
        processed_examples = {}
        for full_name, expected in examples.items():
            parts = full_name.split(' ', 1)
            make = parts[0] if len(parts) > 1 else ''
            model = parts[1] if len(parts) > 1 else parts[0]
            actual = self.create_slug(make, model)
            processed_examples[full_name] = actual

        return processed_examples


def get_camera_slug(camera_make: str = '', camera_model: str = '', custom_mappings: Optional[Dict[str, str]] = None) -> str:
    """
    Convenience function to get a camera slug

    Args:
        camera_make: Camera manufacturer
        camera_model: Camera model name
        custom_mappings: Optional custom name mappings

    Returns:
        Clean slug suitable for file naming
    """
    slugger = CameraSlugger(custom_mappings)
    return slugger.create_slug(camera_make, camera_model)