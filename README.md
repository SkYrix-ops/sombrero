
# Spinning Sombrero Surface
<img width="1378" height="905" alt="2025-12-08_11-27-24" src="https://github.com/user-attachments/assets/a90fbfd5-eafd-4300-915c-453ce6a1ca26" />


An animated ripple surface rendered with Pygame. The mesh spins in place about the Z axis, then receives a camera-like tilt so you see it in perspective. Hidden-line rendering keeps nearer faces in front, and edges are colorized by height using an HSV gradient (low = blue, high = red) to highlight the central peak.

## Install
1) Ensure Python 3.9+ is available.  
2) (Optional) Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
3) Install dependencies:
```bash
pip install -r requirements.txt
```

## Run
```bash
python3 main.py
```
Press `Esc` or close the window to exit.

## How It Works
- The height function is a damped cosine of the radial distance `r = sqrt(x^2 + y^2)`: a wave term `cos(r * freq - t * speed)` multiplied by an exponential decay and a distance-based amplitude falloff. This produces concentric ripples with a pronounced center spike—the classic “sombrero” profile.  
- Each grid point is spun around Z, then tilted about X for presentation, then projected to 2D with a perspective scale factor.  
- Quads are depth-sorted back-to-front (painter’s algorithm) to fill hidden areas with the background color before drawing edge lines.  
- Edge colors come from HSV: the hue is mapped from the absolute height of the two edge endpoints, giving cool colors on low ripples and warm colors on the peak.

## What to Tweak
- `RIPPLE_FREQ`, `RIPPLE_SPEED`, `HEIGHT_SCALE`, `AMPLITUDE_FALLOFF`, and `RIPPLE_DECAY` adjust the shape and motion.  
- `SPIN_RATE` controls how fast the surface spins.  
- `BASE_TILT_X` sets the presentation tilt angle.
