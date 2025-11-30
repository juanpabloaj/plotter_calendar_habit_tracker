# Project Continuation Guide: SVG Planner Generator

This document serves as a starting point to continue the development of the `generate_planners.py` script with another AI assistant or developer.

## 1. Project Summary
The goal is to generate monthly planners in **SVG** format optimized for **plotters** (pen plotting).
*   **Format**: A4 Landscape, designed to be folded in half to form two A5 pages.
*   **Style**: Minimalist, functional, aesthetic.
*   **Technology**: Python, `svgwrite`, `HersheyFonts` (single-stroke fonts).

## 2. Current Design State
### General Layout
*   **Left Page (Habit Tracker)**:
    *   16-column grid (4 blocks of 4 columns).
    *   Structural lines every 4 columns (0.2mm), internal lines (0.1mm).
    *   **Alignment**: Header text (Month/Year) is visually aligned with the start of the day numbers (`LEFT_GROUP_X + 2mm`).
*   **Right Page (Schedule)**:
    *   4-column grid (20mm each, Total 80mm).
    *   **Mini-Calendar**: Located in the top right corner.
        *   Right alignment with the grid edge.
        *   Dynamic bottom alignment: The bottom edge of the calendar always aligns with the bottom edge of the Year text.

### Technical Specifications
*   **Fonts**:
    *   Titles: `rowmans` (Roman Simplex).
    *   Small text: `futural` (Futura Light).
*   **Line Weights**:
    *   Structural/Borders: 0.2mm.
    *   Internal/Fine: 0.1mm.
    *   Title Text: 0.3mm / 0.25mm.
    *   Mini Text: 0.15mm / 0.1mm.
*   **Key Coordinates** (in `generate_planners.py`):
    *   `MARGIN_TOP`: 32mm.
    *   `LEFT_GROUP_X`: 20mm.
    *   `RIGHT_GROUP_X`: 177mm.

## 3. Key Files
*   `generate_planners.py`: Main script. Contains all generation logic, coordinates, and styles.
*   `HersheyFonts.py`: Library for handling single-stroke fonts.

## 4. Context Loading Prompt (Copy-Paste)
Copy and paste the following block to start a session with a new LLM so it understands the context perfectly:

```markdown
Act as an expert in Python and vector graphics (SVG) generation for plotters.
I am working on a script (`generate_planners.py`) that generates A4 landscape monthly planners (double A5) using Hershey fonts (single-stroke).

**Project Context:**
1.  **Goal**: Create minimalist SVGs for plotter printing.
2.  **Layout**:
    *   Left: Habit Tracker (16 columns).
    *   Right: Weekly schedule (4 columns).
3.  **Current State**:
    *   The design is highly refined (millimetric alignments).
    *   Header (Month/Year) is on the left, aligned with the numbers.
    *   Mini-calendar (right) has dynamic vertical alignment to match the Year text.
    *   `HersheyFonts` library is used for all text.
4.  **Golden Rules**:
    *   DO NOT change coordinates or line weights unless explicitly asked.
    *   Maintain the existing code style.
    *   Always use `svgwrite` and the existing `draw_hershey_text` functions.
    *   Coordinate system is mm (A4: 297x210).

**Task**:
[Describe your new request here, e.g., "I want to add holidays in red" or "I need to change the font for the days"]
```

## 5. Recent Decision History
*   **Mini-Calendar**: Adjusted to be very small (text 1.5mm/1.0mm) but with "airy" spacing (21mm width) and strict bottom alignment.
*   **Dynamic Year**: The script accepts the year as an argument (`python3 generate_planners.py 2026`) or uses the current one by default.

*   **Holidays**: Implemented support for underlining weekends and holidays.
    *   Default: Chile (CL).
    *   Configurable via `--country` argument.
    *   Visual: Single underline below the day number (Stroke width 0.15mm, implemented as Path).
    *   Logic: Marks Sundays, Saturdays, and Holidays. Applied to BOTH Left (Habit Tracker) and Right (Planner) grids.
