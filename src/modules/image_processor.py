import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from PIL import Image, ImageEnhance
from PIL.Image import Transpose, Resampling

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.processing_config = config.get('image_processing', {})
        self.auto_rotate = self.processing_config.get('auto_rotate', True)
        self.auto_enhance = self.processing_config.get('auto_enhance', False)
        self.generate_thumbnails = self.processing_config.get('generate_thumbnails', False)
        self.thumbnail_sizes = self.processing_config.get('thumbnail_sizes', [200, 400, 800])

    def process_image(self, image_path: str, metadata: Dict[str, Any],
                     output_path: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """Process image with auto-rotation and optional enhancements"""
        result = {
            'original_path': image_path,
            'processed': False,
            'auto_rotated': False,
            'enhanced': False,
            'thumbnails_created': [],
            'error': None
        }

        try:
            if dry_run:
                result['dry_run'] = True
                result['would_process'] = self._needs_processing(metadata)
                return result

            with Image.open(image_path) as img:
                original_img = img.copy()
                modified = False

                # Auto-rotate based on EXIF orientation
                if self.auto_rotate:
                    rotated_img = self._auto_rotate_image(img, metadata)
                    if rotated_img != img:
                        img = rotated_img
                        modified = True
                        result['auto_rotated'] = True
                        logger.info(f"Auto-rotated image: {image_path}")

                # Auto-enhance if enabled
                if self.auto_enhance:
                    enhanced_img = self._auto_enhance_image(img)
                    if enhanced_img != img:
                        img = enhanced_img
                        modified = True
                        result['enhanced'] = True
                        logger.info(f"Auto-enhanced image: {image_path}")

                # Save processed image if modified
                if modified and output_path:
                    output_path = Path(output_path)
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    # Preserve quality and format
                    save_kwargs = {'quality': 95, 'optimize': True}
                    if img.format == 'JPEG':
                        save_kwargs['exif'] = original_img.info.get('exif', b'')

                    img.save(output_path, **save_kwargs)
                    result['processed'] = True
                    result['output_path'] = str(output_path)

                # Generate thumbnails if enabled
                if self.generate_thumbnails:
                    thumbnails = self._generate_thumbnails(img, image_path, output_path or image_path)
                    result['thumbnails_created'] = thumbnails

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error processing image {image_path}: {e}")

        return result

    def _auto_rotate_image(self, img: Image.Image, metadata: Dict[str, Any]) -> Image.Image:
        """Auto-rotate image based on EXIF orientation"""
        orientation = metadata.get('orientation')

        if not orientation:
            return img

        # EXIF orientation values and corresponding rotations
        orientation_rotations = {
            1: 0,    # Normal
            2: 0,    # Mirrored horizontal
            3: 180,  # Rotated 180°
            4: 180,  # Mirrored vertical
            5: 90,   # Mirrored horizontal + rotated 90° CCW
            6: 270,  # Rotated 90° CW
            7: 270,  # Mirrored horizontal + rotated 90° CW
            8: 90    # Rotated 90° CCW
        }

        rotation = orientation_rotations.get(orientation, 0)

        if rotation != 0:
            img = img.rotate(-rotation, expand=True)
            logger.debug(f"Rotated image {rotation} degrees based on EXIF orientation {orientation}")

        # Handle mirroring
        if orientation in [2, 4, 5, 7]:
            img = img.transpose(Transpose.FLIP_LEFT_RIGHT)
            logger.debug(f"Mirrored image based on EXIF orientation {orientation}")

        return img

    def _auto_enhance_image(self, img: Image.Image) -> Image.Image:
        """Apply basic auto-enhancement to image"""
        try:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Auto-contrast enhancement
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)

            # Auto-brightness adjustment (subtle)
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)

            # Slight color enhancement
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.05)

            return img

        except Exception as e:
            logger.debug(f"Error in auto-enhancement: {e}")
            return img

    def _generate_thumbnails(self, img: Image.Image, original_path: str,
                           output_base_path: str) -> List[str]:
        """Generate thumbnails in multiple sizes"""
        thumbnails = []
        base_path = Path(output_base_path)
        thumb_dir = base_path.parent / 'thumbnails'
        thumb_dir.mkdir(exist_ok=True)

        for size in self.thumbnail_sizes:
            try:
                # Calculate thumbnail size maintaining aspect ratio
                img_copy = img.copy()
                img_copy.thumbnail((size, size), Resampling.LANCZOS)

                # Create thumbnail filename
                thumb_name = f"{base_path.stem}_{size}px{base_path.suffix}"
                thumb_path = thumb_dir / thumb_name

                # Save thumbnail
                save_kwargs = {'quality': 85, 'optimize': True}
                img_copy.save(thumb_path, **save_kwargs)

                thumbnails.append(str(thumb_path))
                logger.debug(f"Created thumbnail: {thumb_path}")

            except Exception as e:
                logger.warning(f"Error creating {size}px thumbnail for {original_path}: {e}")

        return thumbnails

    def _needs_processing(self, metadata: Dict[str, Any]) -> bool:
        """Check if image needs processing based on metadata"""
        needs_rotation = False

        if self.auto_rotate:
            orientation = metadata.get('orientation', 1)
            needs_rotation = orientation != 1

        return needs_rotation or self.auto_enhance or self.generate_thumbnails

    def get_social_media_specs(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific image specifications"""
        specs = {
            'instagram': {
                'square': {'size': (1080, 1080), 'quality': 95},
                'portrait': {'size': (1080, 1350), 'quality': 95},
                'landscape': {'size': (1080, 566), 'quality': 95},
                'story': {'size': (1080, 1920), 'quality': 95}
            },
            'facebook': {
                'post': {'size': (1200, 630), 'quality': 85},
                'cover': {'size': (851, 315), 'quality': 85},
                'profile': {'size': (180, 180), 'quality': 85}
            },
            'twitter': {
                'post': {'size': (1024, 512), 'quality': 85},
                'header': {'size': (1500, 500), 'quality': 85},
                'profile': {'size': (400, 400), 'quality': 85}
            },
            'linkedin': {
                'post': {'size': (1200, 627), 'quality': 85},
                'cover': {'size': (1584, 396), 'quality': 85},
                'profile': {'size': (400, 400), 'quality': 85}
            }
        }

        return specs.get(platform.lower(), {})

    def optimize_for_social_media(self, image_path: str, platform: str,
                                 format_type: str = 'post', output_dir: str = None,
                                 dry_run: bool = False) -> Dict[str, Any]:
        """Optimize image for specific social media platform"""
        result = {
            'original_path': image_path,
            'platform': platform,
            'format_type': format_type,
            'optimized': False,
            'output_path': None,
            'error': None
        }

        try:
            specs = self.get_social_media_specs(platform)
            if not specs or format_type not in specs:
                result['error'] = f"Unsupported platform/format: {platform}/{format_type}"
                return result

            format_specs = specs[format_type]
            target_size = format_specs['size']
            quality = format_specs['quality']

            if dry_run:
                result['dry_run'] = True
                result['would_resize_to'] = target_size
                result['would_set_quality'] = quality
                return result

            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Calculate resize strategy
                img_aspect = img.width / img.height
                target_aspect = target_size[0] / target_size[1]

                if img_aspect > target_aspect:
                    # Image is wider - crop sides
                    new_height = target_size[1]
                    new_width = int(new_height * img_aspect)
                    img = img.resize((new_width, new_height), Resampling.LANCZOS)

                    # Center crop
                    left = (new_width - target_size[0]) // 2
                    img = img.crop((left, 0, left + target_size[0], target_size[1]))
                else:
                    # Image is taller - crop top/bottom
                    new_width = target_size[0]
                    new_height = int(new_width / img_aspect)
                    img = img.resize((new_width, new_height), Resampling.LANCZOS)

                    # Center crop
                    top = (new_height - target_size[1]) // 2
                    img = img.crop((0, top, target_size[0], top + target_size[1]))

                # Generate output path
                if not output_dir:
                    output_dir_path = Path(image_path).parent / 'social_media'
                else:
                    output_dir_path = Path(output_dir)

                output_dir_path.mkdir(exist_ok=True)

                base_name = Path(image_path).stem
                output_path = output_dir_path / f"{base_name}_{platform}_{format_type}.jpg"

                # Save optimized image
                img.save(output_path, 'JPEG', quality=quality, optimize=True)

                result['optimized'] = True
                result['output_path'] = str(output_path)
                result['final_size'] = target_size
                result['final_quality'] = quality

                logger.info(f"Optimized {image_path} for {platform} {format_type}: {output_path}")

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error optimizing image for social media: {e}")

        return result

    def batch_optimize_for_social_media(self, image_paths: List[str], platform: str,
                                       format_type: str = 'post', output_dir: str = None,
                                       dry_run: bool = False) -> List[Dict[str, Any]]:
        """Batch optimize multiple images for social media"""
        results = []

        for image_path in image_paths:
            result = self.optimize_for_social_media(
                image_path, platform, format_type, output_dir, dry_run
            )
            results.append(result)

        return results