import math
import time
from typing import List, Tuple, Optional
import pytweening

class SmartMouse:
    """Base class for intelligent mouse movement with smooth paths."""

    def __init__(self, mouse_controller=None, tween_function=pytweening.easeInOutQuad):
        """
        Initialize SmartMouse.

        Args:
            mouse_controller: Mouse controller instance (e.g., pynput Controller)
            tween_function: Easing function for smooth movement
        """
        self.mouse = mouse_controller
        self.tween = tween_function

    def generate_path(self, start_x: float, start_y: float, end_x: float, end_y: float,
                     steps: int = 50) -> Tuple[List[Tuple[float, float]], List[float]]:
        """
        Generate a smooth path from start to end position.

        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            steps: Number of steps in the path

        Returns:
            Tuple of (path_points, time_deltas)
        """
        path = []
        time_deltas = []

        # Calculate distance and duration
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)

        if distance < 1:
            return [(end_x, end_y)], [0.001]

        # Generate smooth path using tweening
        for i in range(steps + 1):
            t = i / steps

            # Apply easing function
            eased_t = self.tween(t)

            # Calculate intermediate position
            x = start_x + (end_x - start_x) * eased_t
            y = start_y + (end_y - start_y) * eased_t

            path.append((x, y))

            # Calculate time delta based on distance and easing
            if i < steps:
                next_t = (i + 1) / steps
                next_eased_t = self.tween(next_t)
                delta_t = abs(next_eased_t - eased_t) * (distance / 500)  # Base timing
                time_deltas.append(max(0.001, delta_t))

        return path, time_deltas

    def move_to(self, target_x: float, target_y: float, start_x: Optional[float] = None,
                start_y: Optional[float] = None, callback=None) -> List[Tuple[float, float]]:
        """
        Move mouse smoothly to target position.

        Args:
            target_x, target_y: Target coordinates
            start_x, start_y: Starting coordinates (uses current mouse position if None)
            callback: Optional callback function for each position

        Returns:
            List of path points
        """
        # Get starting position
        if start_x is None or start_y is None:
            if self.mouse:
                start_x, start_y = self.mouse.position
            else:
                raise Exception("start_x and start_y must be provided when mouse control is disabled")

        # Generate smooth path
        path, time_deltas = self.generate_path(start_x, start_y, target_x, target_y)

        # Execute movement
        for i, (px, py) in enumerate(path):
            if self.mouse:
                self.mouse.position = (px, py)

            if callback:
                callback(px, py, i)

            # Apply timing
            if i < len(time_deltas):
                time.sleep(time_deltas[i])

        return path


class FastSmartMouse(SmartMouse):
    """Custom SmartMouse class with faster movement speed."""

    def __init__(self, speed_multiplier=0.3, **kwargs):
        """
        Initialize FastSmartMouse with speed control.

        Args:
            speed_multiplier: Multiplier for timing delays (0.1 = 10x faster, 1.0 = normal speed)
            **kwargs: Additional arguments passed to SmartMouse
        """
        super().__init__(**kwargs)
        self.speed_multiplier = max(0.01, speed_multiplier)  # Minimum speed multiplier

    def move_to(self, target_x, target_y, start_x=None, start_y=None, callback=None):
        """Move mouse with faster timing."""
        # Get the normal path and timing
        if start_x is None or start_y is None:
            if self.mouse:
                start_x, start_y = self.mouse.position
            else:
                raise Exception("start_x and start_y must be provided when mouse control is disabled")

        distance = (target_x - start_x) ** 2 + (target_y - start_y) ** 2
        if distance < 1:
            return [(target_x, target_y)]

        # Generate path using parent method but modify timing
        path, time_deltas = self.generate_path(start_x, start_y, target_x, target_y)

        # Apply speed multiplier to reduce timing delays
        fast_time_deltas = [max(0.001, dt * self.speed_multiplier) for dt in time_deltas]

        # Execute movement with faster timing
        for i, (px, py) in enumerate(path):
            if self.mouse:
                self.mouse.position = (px, py)

            if callback:
                callback(px, py, i)

            # Use faster timing
            if i < len(fast_time_deltas):
                import time
                time.sleep(fast_time_deltas[i])

        # Ensure final position is exact
        if self.mouse:
            self.mouse.position = (target_x, target_y)

        return path