# Plotter Habit Tracker

A4 landscape monthly planner generator in SVG format, optimized for plotters (Axidraw, etc.) using Hershey fonts (single stroke).

## Features
- **A4 Landscape Design**: Split into two A5 pages (Habit Tracker on the left, Planner on the right).
- **Single Stroke Fonts**: Uses Hershey fonts for clean plotter strokes.
- **Holidays**: Holiday support (default Chile `CL`), visualized with an underline.
- **Customizable**: Configurable year and country.

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Generate planners (default current year, CL):
   ```bash
   python3 generate_planners.py
   ```
3. Custom options:
   ```bash
   python3 generate_planners.py 2026 US
   ```

SVG files are generated in the `output_YYYY` folder.
