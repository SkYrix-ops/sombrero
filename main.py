import math
from typing import List, Optional, Tuple

import pygame

# Basic window and camera settings
WIDTH, HEIGHT = 960, 720
FPS = 60
FOV = 700
VIEWER_DISTANCE = 90

# Surface geometry
GRID_RADIUS = 28
GRID_STEP = 1
BASE_TILT_X = math.radians(55)  # presentation tilt toward the viewer (applied after spinning)
SPIN_RATE = 0.8  # radians per second around the Z axis

# Wave properties
RIPPLE_FREQ = 0.35
RIPPLE_SPEED = 2.3
RIPPLE_DECAY = 0.025
HEIGHT_SCALE = 4.0

# Colors
BG_COLOR = (10, 12, 18)
LINE_COLOR = (70, 220, 255)


def ripple_height(x: float, y: float, t: float) -> float:
    """Compute the ripple height at (x, y) for time t."""
    r = math.hypot(x, y)
    wave = math.cos(r * RIPPLE_FREQ - t * RIPPLE_SPEED)
    envelope = math.exp(-r * RIPPLE_DECAY)
    return wave * envelope * HEIGHT_SCALE


def generate_grid_points(t: float) -> List[List[Optional[Tuple[float, float]]]]:
    """Generate projected 2D points for the surface mesh at time t."""
    grid_axis = range(-GRID_RADIUS, GRID_RADIUS + 1, GRID_STEP)

    cosx, sinx = math.cos(BASE_TILT_X), math.sin(BASE_TILT_X)
    spin_angle = t * SPIN_RATE
    cosz, sinz = math.cos(spin_angle), math.sin(spin_angle)

    points: List[List[Optional[Tuple[float, float]]]] = []

    for x in grid_axis:
        row: List[Optional[Tuple[float, float]]] = []
        for y in grid_axis:
            z = ripple_height(x, y, t)

            # Spin around the Z axis in place
            x_spin = x * cosz - y * sinz
            y_spin = x * sinz + y * cosz
            z_spin = z

            # Apply the presentation tilt after spinning (camera-like tilt)
            y_tilt = y_spin * cosx - z_spin * sinx
            z_tilt = y_spin * sinx + z_spin * cosx

            depth = VIEWER_DISTANCE + z_tilt
            if depth <= 0.1:
                row.append(None)
                continue

            factor = FOV / depth
            px = x_spin * factor + WIDTH / 2
            py = -y_tilt * factor + HEIGHT / 2
            row.append((px, py))
        points.append(row)

    return points


def draw_mesh(screen: pygame.Surface, points: List[List[Optional[Tuple[float, float]]]]) -> None:
    rows = len(points)
    cols = len(points[0]) if points else 0

    for i in range(rows):
        for j in range(cols):
            if points[i][j] is None:
                continue
            # Connect to the next point in X
            if j + 1 < cols and points[i][j + 1] is not None:
                pygame.draw.aaline(screen, LINE_COLOR, points[i][j], points[i][j + 1])
            # Connect to the next point in Y
            if i + 1 < rows and points[i + 1][j] is not None:
                pygame.draw.aaline(screen, LINE_COLOR, points[i][j], points[i + 1][j])


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spinning Ripple Surface")
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        t = pygame.time.get_ticks() / 1000.0

        screen.fill(BG_COLOR)
        points = generate_grid_points(t)
        draw_mesh(screen, points)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
