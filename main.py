"""
Date: 2025-12-08
Author: Dave Plummer plus AI Assist
Description: Animated spinning ripple surface rendered with Pygame. It samples a
cosine-based height field that decays with distance, spins the mesh about the Z
axis, then applies a presentation tilt for projection. Quads are depth-sorted
for hidden-line removal, and edges are colorized via HSV using height-based
amplitude to map low-to-high elevations across the spectrum.
"""

import math
from typing import List, Optional, Tuple
import pygame, colorsys

WIDTH, HEIGHT = 960, 720  # window size
FPS = 60  # frame cap
FOV = 700  # projection factor
VIEWER_DISTANCE = 90  # camera distance

GRID_RADIUS = 28  # half-size of grid in units
GRID_STEP = 1  # grid resolution
BASE_TILT_X = math.radians(55)  # presentation tilt after spinning
SPIN_RATE = 0.25  # radians per second around Z

RIPPLE_FREQ = 0.65  # ripple density
RIPPLE_SPEED = 4  # ripple time speed
RIPPLE_DECAY = 0.015  # edge damping
HEIGHT_SCALE = 20.0  # base amplitude
AMPLITUDE_FALLOFF = 0.06  # amplitude shrinks with distance

BG_COLOR = (10, 12, 18)  # background
LINE_COLOR = (70, 220, 255)  # fallback line color


def ripple_height(x: float, y: float, t: float) -> float:
    """Compute the ripple height at (x, y) for time t."""
    r = math.hypot(x, y)
    wave = math.cos(r * RIPPLE_FREQ - t * RIPPLE_SPEED)
    envelope = math.exp(-r * RIPPLE_DECAY)
    amplitude = HEIGHT_SCALE / (1.0 + AMPLITUDE_FALLOFF * r)
    return wave * envelope * amplitude


def hsv_to_rgb_int(h: float, s: float, v: float) -> Tuple[int, int, int]:
    """Convert HSV [0,1] floats to 0-255 RGB ints."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


def generate_grid_points(t: float) -> List[List[Optional[Tuple[float, float, float, float]]]]:
    """Generate projected 2D points (plus depth and amplitude) for the surface mesh at time t."""
    grid_axis = range(-GRID_RADIUS, GRID_RADIUS + 1, GRID_STEP)
    cosx, sinx = math.cos(BASE_TILT_X), math.sin(BASE_TILT_X)
    spin_angle = t * SPIN_RATE
    cosz, sinz = math.cos(spin_angle), math.sin(spin_angle)
    points: List[List[Optional[Tuple[float, float, float, float]]]] = []

    for x in grid_axis:
        row: List[Optional[Tuple[float, float, float, float]]] = []
        for y in grid_axis:
            z = ripple_height(x, y, t)
            x_spin = x * cosz - y * sinz  # spin around Z
            y_spin = x * sinz + y * cosz
            z_spin = z
            y_tilt = y_spin * cosx - z_spin * sinx  # presentation tilt
            z_tilt = y_spin * sinx + z_spin * cosx
            depth = VIEWER_DISTANCE + z_tilt
            if depth <= 0.1:
                row.append(None); continue
            factor = FOV / depth
            px = x_spin * factor + WIDTH / 2
            py = -y_tilt * factor + HEIGHT / 2
            amp = abs(z)
            row.append((px, py, depth, amp))
        points.append(row)
    return points


def draw_hidden_line_mesh(screen: pygame.Surface, points: List[List[Optional[Tuple[float, float, float, float]]]]) -> None:
    """Hidden-line style: painter's algorithm filling quads far-to-near, then drawing edges."""
    rows = len(points)
    cols = len(points[0]) if points else 0

    quads: List[Tuple[float, List[Tuple[float, float, float]]]] = []
    for i in range(rows - 1):
        for j in range(cols - 1):
            p00 = points[i][j]
            p10 = points[i + 1][j]
            p11 = points[i + 1][j + 1]
            p01 = points[i][j + 1]
            if None in (p00, p10, p11, p01):
                continue
            p00_xy, p10_xy = (p00[0], p00[1]), (p10[0], p10[1])
            p11_xy, p01_xy = (p11[0], p11[1]), (p01[0], p01[1])
            avg_depth = (p00[2] + p10[2] + p11[2] + p01[2]) / 4.0
            quads.append((avg_depth, [
                (p00_xy[0], p00_xy[1], p00[3]),
                (p10_xy[0], p10_xy[1], p10[3]),
                (p11_xy[0], p11_xy[1], p11[3]),
                (p01_xy[0], p01_xy[1], p01[3]),
            ]))

    quads.sort(key=lambda q: q[0], reverse=True)  # far to near

    for _, corners in quads:
        fill_pts = [(c[0], c[1]) for c in corners]  # corners: (x, y, amp)
        pygame.draw.polygon(screen, BG_COLOR, fill_pts)
        edges = [(corners[0], corners[1]), (corners[1], corners[2]), (corners[2], corners[3]), (corners[3], corners[0])]
        for a, b in edges:
            avg_amp = (a[2] + b[2]) * 0.5
            hue = min(1.0, avg_amp / HEIGHT_SCALE)
            color = hsv_to_rgb_int(hue, 1.0, 1.0)
            pygame.draw.aaline(screen, color, (a[0], a[1]), (b[0], b[1]))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spinning Ripple Surface")
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        t = pygame.time.get_ticks() / 1000.0
        screen.fill(BG_COLOR)
        draw_hidden_line_mesh(screen, generate_grid_points(t))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == "__main__":
    main()
