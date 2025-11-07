import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class DuplicateDetector:
    def __init__(self, config: Dict):
        self.config = config.get("duplicate_detection", {})
        self.method = self.config.get("method", "hash")
        self.threshold = self.config.get("threshold", 0.95)
        self.action = self.config.get("action", "skip")
        self.duplicate_folder = self.config.get("duplicate_folder", "DUPLICATES")
        self.hash_cache = {}

    def find_duplicates(self, file_paths: List[str]) -> Dict[str, List[str]]:
        duplicates = {}

        if self.method == "hash":
            duplicates = self._find_by_hash(file_paths)
        elif self.method == "pixel":
            duplicates = self._find_by_pixels(file_paths)
        elif self.method == "histogram":
            duplicates = self._find_by_histogram(file_paths)

        return duplicates

    def _find_by_hash(self, file_paths: List[str]) -> Dict[str, List[str]]:
        hash_groups = {}

        for file_path in file_paths:
            file_hash = self._calculate_file_hash(file_path)

            if file_hash:
                if file_hash not in hash_groups:
                    hash_groups[file_hash] = []
                hash_groups[file_hash].append(file_path)

        duplicates = {k: v for k, v in hash_groups.items() if len(v) > 1}

        return duplicates

    def _calculate_file_hash(self, file_path: str) -> Optional[str]:
        if file_path in self.hash_cache:
            return self.hash_cache[file_path]

        try:
            hasher = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)

            file_hash = hasher.hexdigest()
            self.hash_cache[file_path] = file_hash
            return file_hash

        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return None

    def _find_by_pixels(self, file_paths: List[str]) -> Dict[str, List[str]]:
        duplicates = {}
        processed = set()
        image_data_cache = {}

        for i, file1 in enumerate(file_paths):
            if file1 in processed:
                continue

            img1_data = self._get_image_array(file1, image_data_cache)
            if img1_data is None:
                continue

            duplicate_group = [file1]

            for file2 in file_paths[i + 1 :]:
                if file2 in processed:
                    continue

                img2_data = self._get_image_array(file2, image_data_cache)
                if img2_data is None:
                    continue

                if self._compare_images(img1_data, img2_data):
                    duplicate_group.append(file2)
                    processed.add(file2)

            if len(duplicate_group) > 1:
                key = f"pixel_group_{len(duplicates)}"
                duplicates[key] = duplicate_group
                processed.add(file1)

        return duplicates

    def _get_image_array(self, file_path: str, cache: Dict) -> Optional[np.ndarray]:
        if file_path in cache:
            return cache[file_path]

        try:
            img = Image.open(file_path)
            img = img.convert("RGB")
            img = img.resize((256, 256))
            img_array = np.array(img)

            cache[file_path] = img_array
            return img_array

        except Exception as e:
            logger.debug(f"Could not load image {file_path}: {e}")
            return None

    def _compare_images(self, img1: np.ndarray, img2: np.ndarray) -> bool:
        try:
            if img1.shape != img2.shape:
                return False

            diff = np.mean(np.abs(img1.astype(float) - img2.astype(float))) / 255.0
            similarity = 1.0 - diff

            return similarity >= self.threshold

        except Exception as e:
            logger.debug(f"Error comparing images: {e}")
            return False

    def _find_by_histogram(self, file_paths: List[str]) -> Dict[str, List[str]]:
        duplicates = {}
        processed = set()
        histogram_cache = {}

        for i, file1 in enumerate(file_paths):
            if file1 in processed:
                continue

            hist1 = self._calculate_histogram(file1, histogram_cache)
            if hist1 is None:
                continue

            duplicate_group = [file1]

            for file2 in file_paths[i + 1 :]:
                if file2 in processed:
                    continue

                hist2 = self._calculate_histogram(file2, histogram_cache)
                if hist2 is None:
                    continue

                if self._compare_histograms(hist1, hist2):
                    duplicate_group.append(file2)
                    processed.add(file2)

            if len(duplicate_group) > 1:
                key = f"histogram_group_{len(duplicates)}"
                duplicates[key] = duplicate_group
                processed.add(file1)

        return duplicates

    def _calculate_histogram(self, file_path: str, cache: Dict) -> Optional[np.ndarray]:
        if file_path in cache:
            return cache[file_path]

        try:
            img = Image.open(file_path)
            img = img.convert("RGB")

            hist_r = np.histogram(np.array(img)[:, :, 0], bins=256, range=(0, 256))[0]
            hist_g = np.histogram(np.array(img)[:, :, 1], bins=256, range=(0, 256))[0]
            hist_b = np.histogram(np.array(img)[:, :, 2], bins=256, range=(0, 256))[0]

            histogram = np.concatenate([hist_r, hist_g, hist_b])

            histogram = histogram / histogram.sum()

            cache[file_path] = histogram
            return histogram

        except Exception as e:
            logger.debug(f"Could not calculate histogram for {file_path}: {e}")
            return None

    def _compare_histograms(self, hist1: np.ndarray, hist2: np.ndarray) -> bool:
        try:
            correlation = np.corrcoef(hist1, hist2)[0, 1]
            return correlation >= self.threshold

        except Exception as e:
            logger.debug(f"Error comparing histograms: {e}")
            return False

    def is_duplicate(self, file1: str, file2: str) -> bool:
        if self.method == "hash":
            hash1 = self._calculate_file_hash(file1)
            hash2 = self._calculate_file_hash(file2)
            return hash1 == hash2 if (hash1 and hash2) else False

        elif self.method == "pixel":
            img1 = self._get_image_array(file1, {})
            img2 = self._get_image_array(file2, {})
            if img1 is not None and img2 is not None:
                return self._compare_images(img1, img2)

        elif self.method == "histogram":
            hist1 = self._calculate_histogram(file1, {})
            hist2 = self._calculate_histogram(file2, {})
            if hist1 is not None and hist2 is not None:
                return self._compare_histograms(hist1, hist2)

        return False

    def handle_duplicate(
        self, original: str, duplicate: str, destination_base: str
    ) -> Tuple[str, str]:
        if self.action == "skip":
            return "skip", f"Skipping duplicate: {duplicate}"

        elif self.action == "rename":
            path = Path(duplicate)
            counter = 1
            new_path = path.parent / f"{path.stem}_dup{counter}{path.suffix}"

            while new_path.exists():
                counter += 1
                new_path = path.parent / f"{path.stem}_dup{counter}{path.suffix}"

            return "rename", str(new_path)

        elif self.action == "move":
            dup_folder = Path(destination_base) / self.duplicate_folder
            dup_folder.mkdir(parents=True, exist_ok=True)
            new_path = dup_folder / Path(duplicate).name

            counter = 1
            while new_path.exists():
                new_path = (
                    dup_folder
                    / f"{Path(duplicate).stem}_{counter}{Path(duplicate).suffix}"
                )
                counter += 1

            return "move", str(new_path)

        return "skip", "Unknown action"

    def clear_cache(self):
        self.hash_cache.clear()
