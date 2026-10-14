import os
from typing import Optional, Tuple, Dict, Any

try:
    import numpy as np
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False
    np = None

try:
    import cv2
    HAS_CV2 = True and HAS_NUMPY
except Exception:
    HAS_CV2 = False

try:
    from PIL import Image
    HAS_PIL = True
except Exception:
    HAS_PIL = False


class VisionEngine:
    def __init__(self, templates_dir: str = "assets/templates"):
        self.templates_dir = templates_dir
        self.templates: Dict[str, Any] = {}
        self.load_templates()

    def load_templates(self):
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            return

        for fname in os.listdir(self.templates_dir):
            if fname.lower().endswith((".png", ".jpg")):
                name = os.path.splitext(fname)[0]
                filepath = os.path.join(self.templates_dir, fname)
                if HAS_CV2 and HAS_NUMPY:
                    img = cv2.imread(filepath, cv2.IMREAD_COLOR)
                elif HAS_PIL:
                    img = Image.open(filepath).convert("RGB")
                else:
                    img = None

                if img is not None:
                    self.templates[name] = img

    def find_template(self, screen: Any, template_name: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        if template_name not in self.templates or screen is None:
            return None

        template = self.templates[template_name]

        if HAS_CV2 and HAS_NUMPY and isinstance(screen, np.ndarray) and isinstance(template, np.ndarray):
            th, tw = template.shape[:2]
            sh, sw = screen.shape[:2]
            if th > sh or tw > sw:
                return None
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            if max_val >= threshold:
                center_x = max_loc[0] + tw // 2
                center_y = max_loc[1] + th // 2
                return int(center_x), int(center_y)

        return None

    def extract_loot_roi(self, screen: Any) -> Dict[str, Any]:
        # Handle PIL Image
        if hasattr(screen, "crop") and hasattr(screen, "size"):
            w, h = screen.size
            scale_x = w / 1280.0
            scale_y = h / 720.0
            return {
                "gold": screen.crop((int(48 * scale_x), int(55 * scale_y), int(230 * scale_x), int(95 * scale_y))),
                "elixir": screen.crop((int(48 * scale_x), int(102 * scale_y), int(230 * scale_x), int(142 * scale_y))),
                "dark_elixir": screen.crop((int(48 * scale_x), int(148 * scale_y), int(230 * scale_x), int(188 * scale_y)))
            }

        # Handle NumPy Array
        if HAS_NUMPY and hasattr(screen, "shape"):
            h, w = screen.shape[:2]
            scale_x = w / 1280.0
            scale_y = h / 720.0
            def get_crop(x1, y1, x2, y2):
                return screen[int(y1 * scale_y):int(y2 * scale_y), int(x1 * scale_x):int(x2 * scale_x)]

            return {
                "gold": get_crop(48, 55, 230, 95),
                "elixir": get_crop(48, 102, 230, 142),
                "dark_elixir": get_crop(48, 148, 230, 188)
            }

        return {"gold": None, "elixir": None, "dark_elixir": None}

    def parse_loot_digits(self, roi: Any) -> int:
        if roi is None:
            return 0

        # Handle PIL Image
        if hasattr(roi, "getdata"):
            try:
                bright_pixels = 0
                for pixel in roi.getdata():
                    # If RGB pixel is bright white
                    if len(pixel) >= 3 and pixel[0] > 180 and pixel[1] > 180 and pixel[2] > 180:
                        bright_pixels += 1
                if bright_pixels > 150:
                    return int(bright_pixels * 850)
            except Exception:
                pass
            return 0

        # Handle NumPy array
        if HAS_NUMPY and hasattr(roi, "shape") and roi.size > 0:
            try:
                is_bright = (roi[:, :, 0] > 180) & (roi[:, :, 1] > 180) & (roi[:, :, 2] > 180)
                bright_pixel_count = np.count_nonzero(is_bright)
                if bright_pixel_count > 150:
                    return int(bright_pixel_count * 850)
            except Exception:
                pass

        return 0
