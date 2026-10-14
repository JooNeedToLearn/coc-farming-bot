import random
import time
from typing import Tuple


class Humanizer:
    def __init__(self, variance: int = 5, min_delay: float = 0.8, max_delay: float = 1.6):
        self.variance = variance
        self.min_delay = min_delay
        self.max_delay = max_delay

    def jitter(self, x: int, y: int, radius: int = 5) -> Tuple[int, int]:
        """Applies Gaussian distribution jitter to tap coordinates."""
        # Gaussian offset with standard deviation = radius / 2
        offset_x = int(random.gauss(0, radius / 2.0))
        offset_y = int(random.gauss(0, radius / 2.0))

        # Clamp offsets to radius boundary
        offset_x = max(-radius, min(radius, offset_x))
        offset_y = max(-radius, min(radius, offset_y))

        return int(x + offset_x), int(y + offset_y)

    def sleep_random(self, custom_min: float = None, custom_max: float = None):
        """Sleeps for a randomized human-like duration."""
        low = custom_min if custom_min is not None else self.min_delay
        high = custom_max if custom_max is not None else self.max_delay
        duration = random.uniform(low, high)
        time.sleep(duration)
