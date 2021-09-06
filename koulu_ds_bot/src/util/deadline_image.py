from io import BytesIO
from typing import Union, List
from PIL import Image, ImageDraw, ImageFont

def create_image(deadline_data: List[dict]) -> bytes:
    header_font_size = 40
    norm_font_size = 12
    top_padding = 10
    left_padding = 20
    header_left_pad = 165
    line_height = 16
    bar_y_offset = 0
    bg = '#81b29a'
    header_color = '#3d405b'
    title_color = '#3d405b'
    bar_bg = '#f4f1de'

    height = top_padding + header_font_size + line_height
    height += len(deadline_data) * (line_height * 3)
    width = 500
    bar_start_x = width / 2
    bar_width = norm_font_size * 2
    bar_length = width - bar_start_x - left_padding - (bar_width / 2)
    max_days = 30

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    header_font = ImageFont.truetype("./src/util/fonts/orange_juice.ttf", header_font_size)
    norm_font = ImageFont.truetype("./src/util/fonts/OpenSans.ttf", norm_font_size)
    bold_font = ImageFont.truetype("./src/util/fonts/OpenSansBold.ttf", norm_font_size)

    # Draw header
    draw.text((header_left_pad, top_padding), "deadlinet", font=header_font, fill=header_color)
    
    # Draw deadline text
    y_pos = top_padding + header_font_size + line_height
    for deadline in deadline_data:
        # COURSE TEXT
        course = deadline['course']
        course = course if len(course) < 32 else course[:32] + '...'
        draw.text(
            (left_padding, y_pos),
            course,
            font=bold_font,
            fill=title_color
        )
        y_pos += line_height
        
        # DATE AND TITLE TEXT
        title = deadline['title']
        title = title if len(title) < 24 else title[:24] + '...'
        draw.text(
            (left_padding, y_pos),
            f'{deadline["date"]} - {title}',
            font=norm_font,
            fill=title_color
        )

        # PROGRES BAR BACKGROUND
        draw.line(
            (
                bar_start_x,
                y_pos + bar_y_offset,
                width - left_padding - (bar_width / 2),
                y_pos + bar_y_offset
            ),
            fill=bar_bg,
            width=bar_width
        )
        color, progress_width = calculate_length_and_color(
            deadline['days_until'],
            max_days,
            bar_length
        )

        # PROGRESS BAR END ROUNDING
        draw.ellipse(
            (
                width - left_padding - bar_width,
                y_pos - bar_width / 2 + 1,
                width - left_padding,
                y_pos + bar_width / 2

            ),
                fill = color if int(deadline['days_until']) > 29 else bar_bg
        )

        # PROGRESS BAR COLOR FILLING
        draw.line(
            (
                bar_start_x,
                y_pos + bar_y_offset,
                bar_start_x + progress_width,
                y_pos + bar_y_offset
            ),
            fill=color,
            width=bar_width
        )

        # PROGRESS BAR START ROUNDING
        draw.ellipse(
            (
                bar_start_x - bar_width / 2,
                y_pos - bar_width / 2 + 1,
                bar_start_x + bar_width / 2,
                y_pos + bar_width / 2

            ),
            fill=color
        )

        # DAYS UNTIL TEXT
        draw.text(
            (
                bar_start_x - (norm_font_size / 2),
                y_pos - (norm_font_size / 2) - 1
            ),
            f'{deadline["days_until"]} pv',
            font=bold_font,
            fill=bg#title_color
        )

        y_pos += line_height * 2

    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes


def calculate_length_and_color(days_until: int,
                               max_days: int,
                               max_length: int
                               ) -> Union[str, float]:
    line_length = min(max_length, days_until / max_days * max_length)
    #r = min(255, int(2 * 255 * (1 - days_until / max_days)))
    #g = min(255, int(2 * 255 * (days_until / max_days)))
    #return (r, g, 0), line_length
    return '#f2cc8f', max(12, line_length)
