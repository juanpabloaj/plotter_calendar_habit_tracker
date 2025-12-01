import svgwrite
from HersheyFonts import HersheyFonts
import calendar
import os
import sys
import datetime
import holidays


def generate_planners(year=2025, country_code="CL", output_dir="output_2025"):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize Holidays
    try:
        # Load holidays for current and next year to cover mini-calendars
        country_holidays = holidays.country_holidays(
            country_code, years=[year, year + 1]
        )
    except Exception as e:
        print(f"Error initializing holidays for {country_code}: {e}")
        country_holidays = {}

    # Initialize Hershey Fonts
    hf_title = HersheyFonts()
    hf_title.load_default_font("rowmans")  # Roman Simplex for Title

    hf_small = HersheyFonts()
    hf_small.load_default_font(
        "futural"
    )  # Futura Light for small text (cleaner, narrower)

    # A4 Landscape dimensions in mm
    WIDTH_MM = 297
    HEIGHT_MM = 210

    # Geometry derived from a4_schedule_habit_tracker.svg
    # Margins (mm)
    MARGIN_TOP = 32  # Lowered by 2mm to match visual alignment
    MARGIN_LEFT = 20

    # Left Page (Habit Tracker) Group Position
    LEFT_GROUP_X = 20
    LEFT_GROUP_Y = 32  # Lowered to 32mm

    # Right Page (Schedule) Group Position
    RIGHT_GROUP_X = 157
    RIGHT_GROUP_Y = 32  # Lowered to 32mm

    # Grid Dimensions
    ROW_HEIGHT = 5

    # Relative offsets within the group (mm)
    REL_X_NUM = 4
    REL_X_INITIAL = 7
    REL_X_GRID_START = 10

    # Left Grid: 16 columns of 5mm (4 blocks of 4) = 80mm width
    LEFT_GRID_COLS = 16
    LEFT_COL_WIDTH = 5
    LEFT_GRID_WIDTH = LEFT_GRID_COLS * LEFT_COL_WIDTH

    # Right Grid: 4 columns of 25mm
    RIGHT_GRID_COLS = 4
    RIGHT_COL_WIDTH = 25
    RIGHT_GRID_WIDTH = RIGHT_GRID_COLS * RIGHT_COL_WIDTH

    # Iterate through months
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        # Filename format: YYYY_MM.svg for easy sorting
        filename = os.path.join(output_dir, f"{year}_{month:02d}.svg")

        dwg = svgwrite.Drawing(
            filename, size=(f"{WIDTH_MM}mm", f"{HEIGHT_MM}mm"), profile="tiny"
        )
        dwg.viewbox(0, 0, WIDTH_MM, HEIGHT_MM)

        # Helper to draw text
        def draw_hershey_text(
            text, x, y, size, font_obj, stroke_width=0.3, align="left"
        ):
            lines = font_obj.lines_for_text(text)
            lines_list = list(lines)

            min_x, max_x = float("inf"), float("-inf")
            min_y, max_y = float("inf"), float("-inf")
            has_points = False

            for line in lines_list:
                for px, py in line:
                    min_x = min(min_x, px)
                    max_x = max(max_x, px)
                    min_y = min(min_y, py)
                    max_y = max(max_y, py)
                    has_points = True

            if not has_points:
                return

            glyph_height = max_y - min_y
            if glyph_height == 0:
                glyph_height = 1
            scale = size / glyph_height
            text_width = (max_x - min_x) * scale

            offset_x = 0
            if align == "left":
                offset_x = -min_x * scale
            elif align == "center":
                offset_x = -min_x * scale - (text_width / 2)
            elif align == "right":
                offset_x = -min_x * scale - text_width

            mid_y = (min_y + max_y) / 2
            offset_y = -mid_y * scale

            path_data = ""
            for line in lines_list:
                if not line:
                    continue
                start_x = line[0][0] * scale + x + offset_x
                start_y = line[0][1] * scale + y + offset_y
                path_data += f"M {start_x:.2f},{start_y:.2f} "
                for px, py in line[1:]:
                    nx = px * scale + x + offset_x
                    ny = py * scale + y + offset_y
                    path_data += f"L {nx:.2f},{ny:.2f} "

            if path_data:
                dwg.add(
                    dwg.path(
                        d=path_data,
                        stroke="black",
                        fill="none",
                        stroke_width=stroke_width,
                    )
                )

        # Helper for Monospaced Numbers
        def draw_number_monospaced(
            num, x_right, y, size, font_obj, stroke_width=0.3
        ):
            s_num = str(num)
            digit_width = size * 0.7  # Increased spacing factor for safety

            # Draw units digit
            draw_hershey_text(
                s_num[-1],
                x_right - (digit_width / 2),
                y,
                size,
                font_obj,
                stroke_width,
                align="center",
            )

            # Draw tens digit if exists
            if len(s_num) > 1:
                draw_hershey_text(
                    s_num[0],
                    x_right - digit_width - (digit_width / 2),
                    y,
                    size,
                    font_obj,
                    stroke_width,
                    align="center",
                )

        def draw_holiday_underline(
            dwg, x_right, y_center, day, stroke_width=0.15
        ):
            # Calculate center based on draw_number_monospaced logic
            # digit_width = size * 0.7 = 1.5 * 0.7 = 1.05
            digit_width = 1.05

            if day < 10:
                center_x = x_right - (digit_width / 2)
            else:
                center_x = x_right - digit_width
                # Balance adjustment for 10-19 (narrow '1')
                if 10 <= day <= 19:
                    center_x += 0.2  # Shift right to balance the visual weight

            # Fixed width 1.6mm (center +/- 0.8) to be compact and balanced
            underline_y = y_center + 1.3
            underline_start_x = center_x - 0.8
            underline_end_x = center_x + 0.8

            dwg.add(
                dwg.path(
                    d=f"M {underline_start_x} {underline_y} L {underline_end_x} {underline_y}",
                    stroke="black",
                    stroke_width=stroke_width,
                )
            )

        # --- Header & Mini Calendar ---

        # Left Page Header: Month and Year
        # Stacked: Month Name (Even Smaller) on top, Year (Tiny) below
        # Aligned to the visual start of the numbers (approx 2mm from group start)
        header_x = LEFT_GROUP_X + 2
        header_y = MARGIN_TOP - 10
        draw_hershey_text(
            month_name,
            header_x,
            header_y,
            3.5,
            hf_title,
            stroke_width=0.3,
            align="left",
        )
        draw_hershey_text(
            str(year),
            header_x,
            header_y + 4,
            2.2,
            hf_title,
            stroke_width=0.25,
            align="left",
        )

        # Right Page: Mini Calendar (Next Month)
        next_month = month + 1
        next_month_year = year
        if next_month > 12:
            next_month = 1
            next_month_year += 1

        def draw_mini_calendar(
            m,
            y,
            start_x,
            start_y,
            width,
            dwg_obj,
            cell_height=2.4,
            country_holidays={},
        ):
            # Title
            m_name = calendar.month_name[m]
            draw_hershey_text(
                f"{m_name} {y}",
                start_x + width / 2,
                start_y - 2,
                1.5,
                hf_small,
                stroke_width=0.15,
                align="center",
            )

            # Days Header
            days = "MTWTFSS"
            col_width = width / 7
            for i, d in enumerate(days):
                draw_hershey_text(
                    d,
                    start_x + i * col_width + col_width / 2,
                    start_y + 1.5,
                    1.0,
                    hf_small,
                    stroke_width=0.1,
                    align="center",
                )

            # Calendar Grid
            cal = calendar.monthcalendar(y, m)
            for r, week in enumerate(cal):
                for c, day_num in enumerate(week):
                    if day_num != 0:
                        cx = start_x + c * col_width + col_width / 2
                        cy = start_y + 4 + r * cell_height
                        draw_hershey_text(
                            str(day_num),
                            cx,
                            cy,
                            1.0,
                            hf_small,
                            stroke_width=0.1,
                            align="center",
                        )

                        # Check for Sunday or Holiday
                        current_date = datetime.date(y, m, day_num)
                        is_saturday = current_date.weekday() == 5  # 5=Saturday
                        is_sunday = current_date.weekday() == 6  # 6=Sunday
                        is_holiday = current_date in country_holidays

                        if is_sunday or is_holiday or is_saturday:
                            # Draw underline
                            # Fixed width 2.0mm (center +/- 1.0) for balance
                            underline_y = cy + 1.2
                            underline_start_x = cx - 0.8
                            underline_end_x = cx + 0.8
                            dwg_obj.add(
                                dwg_obj.path(
                                    d=f"M {underline_start_x} {underline_y} L {underline_end_x} {underline_y}",
                                    stroke="black",
                                    stroke_width=0.15,
                                )
                            )

        # Position Mini Calendar aligned to Right Grid Edge
        # Width 21mm (Intermediate spacing)
        mini_cal_width = 21
        mini_cal_col_width = mini_cal_width / 7
        # Shift right by 2 columns width ("a dos columnas... del límite derecho")
        mini_cal_x = (
            RIGHT_GROUP_X
            + RIGHT_GRID_WIDTH
            - mini_cal_width
            + (2 * mini_cal_col_width)
        )

        # Vertical alignment: Bottom of calendar aligned with bottom of Year text
        # Year text is at MARGIN_TOP - 6 (header_y + 4)
        # Mini-cal last row is at mini_cal_y + 4 + (weeks-1)*cell_height
        # So: mini_cal_y = (MARGIN_TOP - 6) - (4 + (weeks-1)*cell_height)
        cal_next = calendar.monthcalendar(next_month_year, next_month)
        weeks_next = len(cal_next)
        mini_cal_cell_height = 2.4
        mini_cal_y = (MARGIN_TOP - 6) - (
            4 + (weeks_next - 1) * mini_cal_cell_height
        )

        draw_mini_calendar(
            next_month,
            next_month_year,
            mini_cal_x,
            mini_cal_y,
            mini_cal_width,
            dwg,
            cell_height=mini_cal_cell_height,
            country_holidays=country_holidays,
        )

        # --- Grid Calculation ---
        num_days = calendar.monthrange(year, month)[1]

        # --- Left Page (Habit Tracker) ---
        # Vertical Lines
        dwg.add(
            dwg.line(
                start=(LEFT_GROUP_X + REL_X_GRID_START, LEFT_GROUP_Y),
                end=(
                    LEFT_GROUP_X + REL_X_GRID_START,
                    LEFT_GROUP_Y + num_days * ROW_HEIGHT,
                ),
                stroke="black",
                stroke_width=0.2,
            )
        )  # Structural 0.2

        for i in range(1, LEFT_GRID_COLS + 1):
            # User Requirement: 4 Main Blocks (16 cols total).
            # First 3 blocks (cols 1-12) have internal lines.
            # 4th block (cols 13-16) has NO internal lines.
            # Structural lines at 4, 8, 12, 16.

            is_structural = i % 4 == 0
            is_internal = not is_structural

            # Draw if it's structural OR (it's internal AND we are in the first 3 blocks)
            if is_structural or (is_internal and i < 12):
                x = LEFT_GROUP_X + REL_X_GRID_START + i * LEFT_COL_WIDTH
                stroke = 0.2 if is_structural else 0.1
                dwg.add(
                    dwg.line(
                        start=(x, LEFT_GROUP_Y),
                        end=(x, LEFT_GROUP_Y + num_days * ROW_HEIGHT),
                        stroke="black",
                        stroke_width=stroke,
                    )
                )

        # --- Right Page (Schedule) ---
        # Vertical Lines
        dwg.add(
            dwg.line(
                start=(RIGHT_GROUP_X + REL_X_GRID_START, RIGHT_GROUP_Y),
                end=(
                    RIGHT_GROUP_X + REL_X_GRID_START,
                    RIGHT_GROUP_Y + num_days * ROW_HEIGHT,
                ),
                stroke="black",
                stroke_width=0.2,
            )
        )  # Structural 0.2

        for i in range(1, RIGHT_GRID_COLS + 1):
            x = RIGHT_GROUP_X + REL_X_GRID_START + i * RIGHT_COL_WIDTH
            stroke = (
                0.2 if i == RIGHT_GRID_COLS else 0.1
            )  # Structural 0.2, Internal 0.1
            dwg.add(
                dwg.line(
                    start=(x, RIGHT_GROUP_Y),
                    end=(x, RIGHT_GROUP_Y + num_days * ROW_HEIGHT),
                    stroke="black",
                    stroke_width=stroke,
                )
            )

        # --- Rows ---
        for day in range(1, num_days + 1):
            y_pos = LEFT_GROUP_Y + (day - 1) * ROW_HEIGHT
            y_center = y_pos + ROW_HEIGHT / 2
            y_bottom = y_pos + ROW_HEIGHT

            # Date info
            weekday_idx = calendar.weekday(year, month, day)
            day_initial = calendar.day_name[weekday_idx][0]

            # --- Left Page Content ---
            # Day Number (Monospaced, Right Aligned)
            # Size 1.5mm, Futura Light, Stroke 0.2mm
            draw_number_monospaced(
                day,
                LEFT_GROUP_X + REL_X_NUM,
                y_center,
                1.5,
                hf_small,
                stroke_width=0.2,
            )

            # Check for Sunday or Holiday
            current_date = datetime.date(year, month, day)
            is_saturday = current_date.weekday() == 5  # 5=Saturday
            is_sunday = current_date.weekday() == 6  # 6=Sunday
            is_holiday = current_date in country_holidays

            if is_sunday or is_holiday or is_saturday:
                draw_holiday_underline(
                    dwg, LEFT_GROUP_X + REL_X_NUM, y_center, day
                )

            # Day Initial
            draw_hershey_text(
                day_initial,
                LEFT_GROUP_X + REL_X_INITIAL,
                y_center,
                1.5,
                hf_small,
                stroke_width=0.2,
                align="center",
            )

            # Horizontal Line (Left)
            dwg.add(
                dwg.line(
                    start=(LEFT_GROUP_X + REL_X_GRID_START, y_bottom),
                    end=(
                        LEFT_GROUP_X + REL_X_GRID_START + LEFT_GRID_WIDTH,
                        y_bottom,
                    ),
                    stroke="black",
                    stroke_width=0.1,
                )
            )  # Internal 0.1

            # --- Right Page Content ---
            # Day Number
            draw_number_monospaced(
                day,
                RIGHT_GROUP_X + REL_X_NUM,
                y_center,
                1.5,
                hf_small,
                stroke_width=0.2,
            )

            if is_sunday or is_holiday or is_saturday:
                draw_holiday_underline(
                    dwg, RIGHT_GROUP_X + REL_X_NUM, y_center, day
                )

            # Day Initial
            draw_hershey_text(
                day_initial,
                RIGHT_GROUP_X + REL_X_INITIAL,
                y_center,
                1.5,
                hf_small,
                stroke_width=0.2,
                align="center",
            )

            # Horizontal Line (Right)
            dwg.add(
                dwg.line(
                    start=(RIGHT_GROUP_X + REL_X_GRID_START, y_bottom),
                    end=(
                        RIGHT_GROUP_X + REL_X_GRID_START + RIGHT_GRID_WIDTH,
                        y_bottom,
                    ),
                    stroke="black",
                    stroke_width=0.1,
                )
            )  # Internal 0.1

        # Top Border Lines
        dwg.add(
            dwg.line(
                start=(LEFT_GROUP_X + REL_X_GRID_START, LEFT_GROUP_Y),
                end=(
                    LEFT_GROUP_X + REL_X_GRID_START + LEFT_GRID_WIDTH,
                    LEFT_GROUP_Y,
                ),
                stroke="black",
                stroke_width=0.2,
            )
        )  # Structural 0.2
        dwg.add(
            dwg.line(
                start=(RIGHT_GROUP_X + REL_X_GRID_START, RIGHT_GROUP_Y),
                end=(
                    RIGHT_GROUP_X + REL_X_GRID_START + RIGHT_GRID_WIDTH,
                    RIGHT_GROUP_Y,
                ),
                stroke="black",
                stroke_width=0.2,
            )
        )  # Structural 0.2

        dwg.save()
        print(f"Generated {filename}")


if __name__ == "__main__":
    # Default to current year
    target_year = datetime.datetime.now().year
    target_country = "CL"

    # Check for command line arguments
    # Usage: python3 generate_planners.py [year] [country_code]
    if len(sys.argv) > 1:
        try:
            target_year = int(sys.argv[1])
        except ValueError:
            print(
                f"Invalid year provided: {sys.argv[1]}. Using default: {target_year}"
            )

    if len(sys.argv) > 2:
        target_country = sys.argv[2].upper()

    output_directory = f"output_{target_year}"
    print(
        f"Generating planners for year {target_year}, country {target_country} in {output_directory}..."
    )
    generate_planners(
        year=target_year,
        country_code=target_country,
        output_dir=output_directory,
    )
