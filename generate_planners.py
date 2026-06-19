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
    REL_X_WEEK_NUM_RIGHT = (
        0  # Week number anchor for right page, pushed further left for spacing
    )

    # Left Grid: 16 columns of 5mm (4 blocks of 4) = 80mm width
    LEFT_GRID_COLS = 16
    LEFT_COL_WIDTH = 5
    LEFT_GRID_WIDTH = LEFT_GRID_COLS * LEFT_COL_WIDTH

    # Right Grid: 4 columns of 25mm
    RIGHT_GRID_COLS = 4
    RIGHT_COL_WIDTH = 25
    RIGHT_GRID_WIDTH = RIGHT_GRID_COLS * RIGHT_COL_WIDTH

    def draw_hershey_text(
        dwg_obj, text, x, y, size, font_obj, stroke_width=0.3, align="left"
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
            dwg_obj.add(
                dwg_obj.path(
                    d=path_data,
                    stroke="black",
                    fill="none",
                    stroke_width=stroke_width,
                )
            )

    def draw_number_monospaced(
        dwg_obj, num, x_right, y, size, font_obj, stroke_width=0.3
    ):
        s_num = str(num)
        digit_width = size * 0.7  # Increased spacing factor for safety

        draw_hershey_text(
            dwg_obj,
            s_num[-1],
            x_right - (digit_width / 2),
            y,
            size,
            font_obj,
            stroke_width,
            align="center",
        )

        if len(s_num) > 1:
            draw_hershey_text(
                dwg_obj,
                s_num[0],
                x_right - digit_width - (digit_width / 2),
                y,
                size,
                font_obj,
                stroke_width,
                align="center",
            )

    def draw_holiday_underline(
        dwg_obj, x_right, y_center, day, stroke_width=0.15
    ):
        digit_width = 1.05

        if day < 10:
            center_x = x_right - (digit_width / 2)
        else:
            center_x = x_right - digit_width
            if 10 <= day <= 19:
                center_x += 0.2  # Shift right to balance the visual weight

        underline_y = y_center + 1.3
        underline_start_x = center_x - 0.8
        underline_end_x = center_x + 0.8

        dwg_obj.add(
            dwg_obj.path(
                d=f"M {underline_start_x} {underline_y} L {underline_end_x} {underline_y}",
                stroke="black",
                stroke_width=stroke_width,
            )
        )

    def draw_mini_calendar(
        dwg_obj,
        m,
        y,
        start_x,
        start_y,
        width,
        cell_height=2.4,
        country_holidays=None,
    ):
        if country_holidays is None:
            country_holidays = {}

        m_name = calendar.month_name[m]
        draw_hershey_text(
            dwg_obj,
            f"{m_name} {y}",
            start_x + width / 2,
            start_y - 2,
            1.5,
            hf_small,
            stroke_width=0.15,
            align="center",
        )

        days = "MTWTFSS"
        col_width = width / 7
        for i, d in enumerate(days):
            draw_hershey_text(
                dwg_obj,
                d,
                start_x + i * col_width + col_width / 2,
                start_y + 1.5,
                1.0,
                hf_small,
                stroke_width=0.1,
                align="center",
            )

        cal = calendar.monthcalendar(y, m)
        for r, week in enumerate(cal):
            for c, day_num in enumerate(week):
                if day_num != 0:
                    cx = start_x + c * col_width + col_width / 2
                    cy = start_y + 4 + r * cell_height
                    draw_hershey_text(
                        dwg_obj,
                        str(day_num),
                        cx,
                        cy,
                        1.0,
                        hf_small,
                        stroke_width=0.1,
                        align="center",
                    )

                    current_date = datetime.date(y, m, day_num)
                    is_saturday = current_date.weekday() == 5  # 5=Saturday
                    is_sunday = current_date.weekday() == 6  # 6=Sunday
                    is_holiday = current_date in country_holidays

                    if is_sunday or is_holiday or is_saturday:
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

    # Iterate through months
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        # Filename format: YYYY_MM.svg for easy sorting
        filename = os.path.join(output_dir, f"{year}_{month:02d}.svg")

        dwg = svgwrite.Drawing(
            filename, size=(f"{WIDTH_MM}mm", f"{HEIGHT_MM}mm"), profile="tiny"
        )
        dwg.viewbox(0, 0, WIDTH_MM, HEIGHT_MM)

        # --- Grid Calculation ---
        num_days = calendar.monthrange(year, month)[1]

        # ====================================================================
        # PLOTTER PATH ORDER: draw the ENTIRE left page first, then the
        # ENTIRE right page. This keeps the pen on one half of the sheet at a
        # time instead of jumping left<->right on every row, which avoids
        # smudges/scratches and reduces total plotting time.
        # ====================================================================

        # ====================================================================
        # LEFT PAGE (Habit Tracker)
        # ====================================================================

        # Left Page Header: Month and Year
        # Stacked: Month Name (Even Smaller) on top, Year (Tiny) below
        # Aligned to the visual start of the numbers (approx 2mm from group start)
        header_x = LEFT_GROUP_X + 2
        header_y = MARGIN_TOP - 10
        draw_hershey_text(
            dwg,
            month_name,
            header_x,
            header_y,
            3.5,
            hf_title,
            stroke_width=0.3,
            align="left",
        )
        draw_hershey_text(
            dwg,
            str(year),
            header_x,
            header_y + 4,
            2.2,
            hf_title,
            stroke_width=0.25,
            align="left",
        )

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

        # Rows (Left): numbers, initials, holiday underlines, horizontal lines
        for day in range(1, num_days + 1):
            y_pos = LEFT_GROUP_Y + (day - 1) * ROW_HEIGHT
            y_center = y_pos + ROW_HEIGHT / 2
            y_bottom = y_pos + ROW_HEIGHT

            # Date info
            current_date = datetime.date(year, month, day)
            weekday_idx = current_date.weekday()
            day_initial = calendar.day_name[weekday_idx][0]

            is_saturday = current_date.weekday() == 5  # 5=Saturday
            is_sunday = current_date.weekday() == 6  # 6=Sunday
            is_holiday = current_date in country_holidays

            # Day Number (Monospaced, Right Aligned)
            # Size 1.5mm, Futura Light, Stroke 0.2mm
            draw_number_monospaced(
                dwg,
                day,
                LEFT_GROUP_X + REL_X_NUM,
                y_center,
                1.5,
                hf_small,
                stroke_width=0.2,
            )

            # Underline for Sunday / Saturday / Holiday
            if is_sunday or is_holiday or is_saturday:
                draw_holiday_underline(
                    dwg, LEFT_GROUP_X + REL_X_NUM, y_center, day
                )

            # Day Initial
            draw_hershey_text(
                dwg,
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

        # Top Border Line (Left)
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

        # ====================================================================
        # RIGHT PAGE (Schedule)
        # ====================================================================

        # Right Page: Mini Calendar (Next Month)
        next_month = month + 1
        next_month_year = year
        if next_month > 12:
            next_month = 1
            next_month_year += 1

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
            dwg,
            next_month,
            next_month_year,
            mini_cal_x,
            mini_cal_y,
            mini_cal_width,
            cell_height=mini_cal_cell_height,
            country_holidays=country_holidays,
        )

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

        # Rows (Right): week number [disabled], numbers, initials,
        # underlines, horizontal lines
        for day in range(1, num_days + 1):
            y_pos = LEFT_GROUP_Y + (day - 1) * ROW_HEIGHT
            y_center = y_pos + ROW_HEIGHT / 2
            y_bottom = y_pos + ROW_HEIGHT

            # Date info
            current_date = datetime.date(year, month, day)
            weekday_idx = current_date.weekday()
            day_initial = calendar.day_name[weekday_idx][0]

            is_saturday = current_date.weekday() == 5  # 5=Saturday
            is_sunday = current_date.weekday() == 6  # 6=Sunday
            is_holiday = current_date in country_holidays

            # Day Number
            if weekday_idx == 0 and False:
                week_number = current_date.isocalendar()[1]
                draw_number_monospaced(
                    dwg,
                    week_number,
                    RIGHT_GROUP_X + REL_X_WEEK_NUM_RIGHT,
                    y_center,
                    1.2,
                    hf_small,
                    stroke_width=0.16,
                )

            draw_number_monospaced(
                dwg,
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
                dwg,
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

        # Top Border Line (Right)
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

    # --- Year Overview (12 months, 6 per side) ---
    overview_filename = os.path.join(output_dir, f"{year}_all_months.svg")
    overview_dwg = svgwrite.Drawing(
        overview_filename,
        size=(f"{WIDTH_MM}mm", f"{HEIGHT_MM}mm"),
        profile="tiny",
    )
    overview_dwg.viewbox(0, 0, WIDTH_MM, HEIGHT_MM)

    OVERVIEW_MARGIN_X = 10
    OVERVIEW_MARGIN_Y = 10
    CENTER_GUTTER = 12
    SIDE_GUTTER_X = 6
    SIDE_GUTTER_Y = 8
    SIDE_COLS = 2
    SIDE_ROWS = 3

    side_width = (WIDTH_MM - (2 * OVERVIEW_MARGIN_X) - CENTER_GUTTER) / 2
    side_height = HEIGHT_MM - (2 * OVERVIEW_MARGIN_Y)
    cell_width = (side_width - SIDE_GUTTER_X) / SIDE_COLS
    cell_height = (side_height - (SIDE_ROWS - 1) * SIDE_GUTTER_Y) / SIDE_ROWS

    cell_padding_x = 2
    cell_padding_top = 4
    cell_padding_bottom = 4

    draw_hershey_text(
        overview_dwg,
        str(year),
        OVERVIEW_MARGIN_X + (side_width / 2),
        OVERVIEW_MARGIN_Y - 3,
        3.0,
        hf_title,
        stroke_width=0.3,
        align="center",
    )

    for month in range(1, 13):
        side_index = 0 if month <= 6 else 1
        month_index = (month - 1) % 6
        row = month_index // SIDE_COLS
        col = month_index % SIDE_COLS

        side_x = OVERVIEW_MARGIN_X + side_index * (side_width + CENTER_GUTTER)
        x = side_x + col * (cell_width + SIDE_GUTTER_X)
        y = OVERVIEW_MARGIN_Y + row * (cell_height + SIDE_GUTTER_Y)

        cal_width = cell_width - (2 * cell_padding_x)
        cal_height = cell_height - (cell_padding_top + cell_padding_bottom)
        available_cell_height = (cal_height - 4) / 5
        ideal_cell_height = cal_width / 7
        mini_cell_height = min(ideal_cell_height, available_cell_height)
        if mini_cell_height < 1.6:
            mini_cell_height = 1.6
        actual_height = 4 + 5 * mini_cell_height
        cal_start_y = y + cell_padding_top + (cal_height - actual_height) / 2

        draw_mini_calendar(
            overview_dwg,
            month,
            year,
            x + cell_padding_x,
            cal_start_y,
            cal_width,
            cell_height=mini_cell_height,
            country_holidays=country_holidays,
        )

    overview_dwg.save()
    print(f"Generated {overview_filename}")


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
