import cv2
import numpy as np
import os
from typing import Optional, Tuple, Dict, Any


class VisionEngine:
    def __init__(self, templates_dir: str = "assets/templates"):
        self.templates_dir = templates_dir
        self.templates: Dict[str, np.ndarray] = {}
        self.load_templates()

    def load_templates(self):
        """Loads all .png templates from the templates directory."""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            return

        for fname in os.listdir(self.templates_dir):
            if fname.lower().endswith((".png", ".jpg")):
                name = os.path.splitext(fname)[0]
                filepath = os.path.join(self.templates_dir, fname)
                img = cv2.imread(filepath, cv2.IMREAD_COLOR)
                if img is not None:
                    self.templates[name] = img

    def find_template(self, screen: np.ndarray, template_name: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """Finds a template within screen and returns center coordinate (x, y) if matched."""
        if template_name not in self.templates or screen is None:
            return None

        template = self.templates[template_name]
        th, tw = template.shape[:2]
        sh, sw = screen.shape[:2]

        if th > sh or tw > sw:
            return None

        # Template matching using normalized cross correlation
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            center_x = max_loc[0] + tw // 2
            center_y = max_loc[1] + th // 2
            return int(center_x), int(center_y)

        return None

    def extract_loot_roi(self, screen: np.ndarray) -> Dict[str, np.ndarray]:
        """Extracts regions of interest for Gold, Elixir, and Dark Elixir numbers (1280x720 base)."""
        h, w = screen.shape[:2]

        # Normalized coordinates relative to 1280x720
        scale_x = w / 1280.0
        scale_y = h / 720.0

        def get_crop(x1, y1, x2, y2):
            return screen[int(y1 * scale_y):int(y2 * scale_y), int(x1 * scale_x):int(x2 * scale_x)]

        # Typical bounding boxes for loot text in scouting mode
        gold_roi = get_crop(48, 55, 230, 95)
        elixir_roi = get_crop(48, 102, 230, 142)
        dark_roi = get_crop(48, 148, 230, 188)

        return {
            "gold": gold_roi,
            "elixir": elixir_roi,
            "dark_elixir": dark_roi
        }

    def parse_loot_digits(self, roi_bgr: np.ndarray) -> int:
        """Parses numeric value from white/bright digit ROI."""
        if roi_bgr is None or roi_bgr.size == 0:
            return 0

        # Convert to grayscale & threshold bright white text (CoC loot numbers)
        gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        # Basic OCR fallback using pytesseract if available, or contour analysis
        try:
            import pytesseract
            text = pytesseract.image_to_string(thresh, config="--psm 7 -c tessedit_char_whitelist=0123456789")
            digits = "".join([c for c in text if c.isdigit()])
            if digits:
                return int(digits)
        except Exception:
            pass

        return 0
