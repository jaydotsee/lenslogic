import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.default_config_path = Path(__file__).parent.parent.parent / "config" / "default_config.yaml"
        self.user_config_path = Path.home() / ".lenslogic" / "config.yaml"
        self.load_config()

    def load_config(self) -> None:
        self.config = self._load_default_config()

        user_config = self._load_user_config()
        if user_config:
            self.config = self._merge_configs(self.config, user_config)

        if self.config_path:
            custom_config = self._load_custom_config()
            if custom_config:
                self.config = self._merge_configs(self.config, custom_config)

    def _load_default_config(self) -> Dict[str, Any]:
        try:
            with open(self.default_config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.warning(f"Default config not found at {self.default_config_path}")
            return self._get_hardcoded_defaults()
        except yaml.YAMLError as e:
            logger.error(f"Error parsing default config: {e}")
            return self._get_hardcoded_defaults()

    def _load_user_config(self) -> Optional[Dict[str, Any]]:
        if not self.user_config_path.exists():
            return None

        try:
            with open(self.user_config_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing user config: {e}")
            return None

    def _load_custom_config(self) -> Optional[Dict[str, Any]]:
        if not self.config_path or not Path(self.config_path).exists():
            return None

        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing custom config: {e}")
            return None

    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def _get_hardcoded_defaults(self) -> Dict[str, Any]:
        return {
            "general": {
                "source_directory": ".",
                "destination_directory": "./organized",
                "dry_run": False,
                "verbose": True,
                "preserve_originals": True,
                "skip_duplicates": True,
                "log_file": "lenslogic.log"
            },
            "file_types": {
                "images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp", "heic", "heif"],
                "raw": ["raw", "cr2", "cr3", "nef", "arw", "orf", "dng", "raf", "rw2", "pef", "srw", "x3f"],
                "videos": ["mp4", "avi", "mov", "mkv", "wmv", "flv", "webm", "m4v", "mpg", "mpeg"]
            },
            "organization": {
                "folder_structure": "{year}/{month:02d}/{day:02d}",
                "separate_raw": True,
                "raw_folder": "RAW",
                "jpg_folder": "JPG",
                "video_folder": "VIDEOS",
                "unknown_folder": "UNKNOWN"
            },
            "naming": {
                "pattern": "{year}{month:02d}{day:02d}_{hour:02d}{minute:02d}{second:02d}_{camera}_{original_name}",
                "include_sequence": True,
                "sequence_padding": 3,
                "lowercase_extension": True
            },
            "features": {
                "extract_gps": True,
                "create_sidecar": True,
                "generate_thumbnails": False,
                "detect_faces": False,
                "auto_rotate": True,
                "remove_duplicates": True
            },
            "geolocation": {
                "enabled": True,
                "reverse_geocode": True,
                "add_location_to_folder": False,
                "cache_lookups": True
            },
            "duplicate_detection": {
                "method": "hash",
                "threshold": 0.95,
                "action": "skip",
                "duplicate_folder": "DUPLICATES"
            }
        }

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any) -> None:
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def save_user_config(self) -> None:
        self.user_config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.user_config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Configuration saved to {self.user_config_path}")

    def export_config(self, path: str) -> None:
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

        logger.info(f"Configuration exported to {path}")

    def update_from_args(self, args: Dict[str, Any]) -> None:
        if args.get('source'):
            self.set('general.source_directory', args['source'])
        if args.get('destination'):
            self.set('general.destination_directory', args['destination'])
        if args.get('dry_run') is not None:
            self.set('general.dry_run', args['dry_run'])
        if args.get('verbose') is not None:
            self.set('general.verbose', args['verbose'])
        if args.get('pattern'):
            self.set('naming.pattern', args['pattern'])
        if args.get('folder_structure'):
            self.set('organization.folder_structure', args['folder_structure'])
        if args.get('create_xmp') is not None:
            self.set('features.create_sidecar', args['create_xmp'])
        if args.get('no_xmp') is not None:
            self.set('features.create_sidecar', not args['no_xmp'])