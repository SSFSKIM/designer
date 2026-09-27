#!/usr/bin/env python3.12
"""Bounded, cheap PNG export for W41 eye sheets: renderCell()'s standalone HTML on stdin,
one composited PNG on stdout. No browser, no native/capture PNG read of its own — every
byte this script touches was already embedded as a data: URI by the authorized renderer
(sheets.ts). This is a rendering convenience, not a new capture or native-reader path.

Parsing is deliberately strict rather than best-effort: renderCell() always emits the same
fixed 2-row x 3-column table (Native | Shipped WebGPU | Candidate, then a bare
"Difference from native" label cell beside the two ΔE panels), so anything that does not
match that exact shape is refused outright. A cell is never silently dropped; the whole
document is refused instead, on stderr, with a non-zero exit.

Every embedded <img> is decoded and pasted onto the output canvas at its own pixel
dimensions, never resized: Image.paste() is a byte copy, and the declared width/height
attributes are cross-checked against the actually-decoded PNG so a lying attribute refuses
rather than silently mis-sizing a cell.
"""
import base64
import binascii
import io
import sys
from html.parser import HTMLParser

from PIL import Image, ImageDraw, ImageFont

# --- Palette / metrics -------------------------------------------------------------------
# Matches sheets.ts's own stylesheet exactly: body{color:#111;background:white}.
BG = (255, 255, 255)
FG = (0x11, 0x11, 0x11)
BORDER_COLOR = (0xaa, 0xaa, 0xaa)

MARGIN = 24
TITLE_GAP = 16
LABEL_GAP = 6
CELL_PADDING = 10
CELL_BORDER = 1
CELL_SPACING = 12
FOOTER_GAP = 18

TITLE_FONT_SIZE = 22
LABEL_FONT_SIZE = 16
BODY_FONT_SIZE = 14

# A compact restatement of sheets.ts's own ΔE prose. PNGs are inspected directly rather than
# in a browser, so the scale has to survive export even though the surrounding <p> prose
# (which carries the full sentence in the HTML) is not otherwise reproduced here.
DELTA_E_FOOTER = 'ΔE × 8 (OKLab distance): black = 0, white = 0.125 or greater (clipped).'

# Fonts shipped with macOS itself; nothing here is downloaded or bundled.
_FONT_CANDIDATES = (
    '/System/Library/Fonts/Helvetica.ttc',
    '/System/Library/Fonts/HelveticaNeue.ttc',
    '/System/Library/Fonts/Supplemental/Arial.ttf',
    '/Library/Fonts/Arial.ttf',
)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    last_error = None
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError as exc:
            last_error = exc
    raise RuntimeError(f'no macOS system font found among {_FONT_CANDIDATES}') from last_error


def default_fonts():
    return {
        'title': load_font(TITLE_FONT_SIZE),
        'label': load_font(LABEL_FONT_SIZE),
        'body': load_font(BODY_FONT_SIZE),
    }


def text_metrics(font: ImageFont.FreeTypeFont, text: str):
    """(width, height, bearing_x, bearing_y). Drawing at (x - bearing_x, y - bearing_y)
    puts the ink's top-left corner exactly at (x, y), so allocating (width, height) starting
    at (x, y) never clips."""
    left, top, right, bottom = font.getbbox(text)
    return right - left, bottom - top, left, top


# --- HTML tree ---------------------------------------------------------------------------
_VOID_TAGS = frozenset({'meta', 'img', 'br', 'hr', 'input', 'link'})


class _Node:
    __slots__ = ('tag', 'attrs', 'children')

    def __init__(self, tag, attrs):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node('#root', {})
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in _VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(_Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        raise ValueError(f'unmatched closing tag </{tag}>')

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def _text_of(node: _Node) -> str:
    parts = []
    for child in node.children:
        parts.append(child if isinstance(child, str) else _text_of(child))
    return ''.join(parts)


def _elements(node: _Node, tag: str):
    return [c for c in node.children if isinstance(c, _Node) and c.tag == tag]


def _non_blank_children(node: _Node):
    return [c for c in node.children
            if not (isinstance(c, str) and c.strip() == '')]


_PNG_DATA_URI_PREFIX = 'data:image/png;base64,'


def _parse_image(img: _Node):
    if 'width' not in img.attrs or 'height' not in img.attrs:
        raise ValueError('<img> is missing width/height attributes')
    try:
        declared_width = int(img.attrs['width'])
        declared_height = int(img.attrs['height'])
    except ValueError as exc:
        raise ValueError('<img> width/height attributes are not integers') from exc
    src = img.attrs.get('src', '')
    if not src.startswith(_PNG_DATA_URI_PREFIX):
        raise ValueError('<img> src is not an embedded image/png data URI')
    b64 = src[len(_PNG_DATA_URI_PREFIX):]
    try:
        png_bytes = base64.b64decode(b64, validate=True)
    except binascii.Error as exc:
        raise ValueError('<img> src base64 payload is malformed') from exc
    try:
        with Image.open(io.BytesIO(png_bytes)) as probe:
            probe.load()
            actual_size = probe.size
    except Exception as exc:  # noqa: BLE001 - any decode failure refuses the whole document
        raise ValueError('<img> src does not decode to a valid PNG') from exc
    if actual_size != (declared_width, declared_height):
        raise ValueError(
            f'<img> declared {declared_width}x{declared_height} but the embedded PNG is '
            f'{actual_size[0]}x{actual_size[1]}')
    return declared_width, declared_height, png_bytes


def _parse_td(td: _Node):
    kids = _non_blank_children(td)
    if len(kids) == 1 and isinstance(kids[0], str):
        return {'kind': 'label', 'text': kids[0].strip()}
    if len(kids) == 2 and isinstance(kids[0], _Node) and kids[0].tag == 'h2' and isinstance(kids[1], _Node):
        label = _text_of(kids[0]).strip()
        content = kids[1]
        if content.tag == 'img':
            width, height, png_bytes = _parse_image(content)
            return {'kind': 'image', 'label': label, 'width': width, 'height': height, 'png': png_bytes}
        if content.tag == 'p':
            return {'kind': 'missing', 'label': label, 'text': _text_of(content).strip()}
        raise ValueError(f'<td> content after <h2> is unexpected: <{content.tag}>')
    raise ValueError('<td> does not match a Native/Shipped/Candidate/ΔE panel shape')


def parse_sheet(html_text: str):
    """Strict structural parse of renderCell()'s exact fixed shape. Raises ValueError on any
    deviation; never silently drops a cell for a malformed or foreign document."""
    builder = _TreeBuilder()
    try:
        builder.feed(html_text)
        builder.close()
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001 - any parser failure refuses the document
        raise ValueError(f'HTML did not parse: {exc}') from exc
    if len(builder.stack) != 1:
        unclosed = ', '.join(f'<{n.tag}>' for n in builder.stack[1:])
        raise ValueError(f'unclosed tag(s): {unclosed}')

    html_nodes = _elements(builder.root, 'html')
    if len(html_nodes) != 1:
        raise ValueError(f'expected exactly one <html> element, found {len(html_nodes)}')
    html_node = html_nodes[0]

    h1_nodes = _elements(html_node, 'h1')
    if len(h1_nodes) != 1:
        raise ValueError(f'expected exactly one <h1> title, found {len(h1_nodes)}')
    title = _text_of(h1_nodes[0]).strip()

    table_nodes = _elements(html_node, 'table')
    if len(table_nodes) != 1:
        raise ValueError(f'expected exactly one <table>, found {len(table_nodes)}')
    table = table_nodes[0]
    if table.attrs.get('aria-label') != 'Native and WebGPU comparison':
        raise ValueError('table is not the expected Native/WebGPU comparison sheet (aria-label mismatch)')

    trs = _elements(table, 'tr')
    if len(trs) != 2:
        raise ValueError(f'expected exactly 2 table rows, found {len(trs)}')
    rows = []
    for tr in trs:
        tds = _elements(tr, 'td')
        if len(tds) != 3:
            raise ValueError(f'expected exactly 3 cells per row, found {len(tds)}')
        rows.append([_parse_td(td) for td in tds])

    for col, cell in enumerate(rows[0]):
        if cell['kind'] == 'label':
            raise ValueError(f'top row column {col} must carry an h2 panel, not a bare label')
    if rows[1][0]['kind'] != 'label':
        raise ValueError('bottom-left cell must be the bare "Difference from native" label')
    for col, cell in enumerate(rows[1][1:], start=1):
        if cell['kind'] == 'label':
            raise ValueError(f'bottom row column {col} must carry an h2 ΔE panel, not a bare label')

    return {'title': title, 'rows': rows}


# --- Layout ------------------------------------------------------------------------------
def compute_layout(sheet, fonts):
    label_font, body_font, title_font = fonts['label'], fonts['body'], fonts['title']
    n_rows, n_cols = 2, 3
    meta = [[None] * n_cols for _ in range(n_rows)]
    # The fixed table's own labels are not uniform in shape: "Shipped WebGPU" and
    # "Shipped ΔE × 8" carry a descending 'p', while "Native", "Candidate" and
    # "Candidate ΔE × 8" do not. A per-cell TIGHT ink bbox height therefore differs by a few
    # pixels between columns of the same row; using it to place the content below each label
    # would invent a visible vertical offset between panels that are supposed to be
    # pixel-comparable (found by inspection of an actual exported sheet). Every label line
    # instead reserves the SAME height everywhere: the font's own ascent+descent, widened
    # further if any actual label's tight bbox is somehow taller than that (so a future label
    # string can only grow the reservation, never silently reintroduce clipping).
    label_ascent, label_descent = label_font.getmetrics()
    label_line_h = label_ascent + label_descent
    for r in range(n_rows):
        for c in range(n_cols):
            cell = sheet['rows'][r][c]
            if cell['kind'] == 'label':
                w, h, bx, by = text_metrics(label_font, cell['text'])
                label_line_h = max(label_line_h, h)
                meta[r][c] = {'kind': 'label', 'text': cell['text'], 'font': label_font,
                              'bearing': (bx, by), 'content_w': w, 'content_h': h}
                continue
            lw, lh, lbx, lby = text_metrics(label_font, cell['label'])
            label_line_h = max(label_line_h, lh)
            if cell['kind'] == 'image':
                iw, ih = cell['width'], cell['height']
                meta[r][c] = {'kind': 'image', 'label': cell['label'], 'label_w': lw,
                              'label_bearing': (lbx, lby), 'image_w': iw, 'image_h': ih,
                              'png': cell['png'], 'content_w': max(lw, iw), 'content_h_tail': ih}
            else:
                tw, th, tbx, tby = text_metrics(body_font, cell['text'])
                meta[r][c] = {'kind': 'missing', 'label': cell['label'], 'label_w': lw,
                              'label_bearing': (lbx, lby), 'text': cell['text'], 'text_w': tw, 'text_h': th,
                              'text_bearing': (tbx, tby), 'content_w': max(lw, tw), 'content_h_tail': th}

    # Second pass: label_line_h is now final (the max over the whole sheet), so every
    # image/missing-text cell's content_h uses that ONE shared value, not its own label's
    # tight height. This is what makes every content start in a row land on the same y.
    for r in range(n_rows):
        for c in range(n_cols):
            m = meta[r][c]
            if m['kind'] != 'label':
                m['content_h'] = label_line_h + LABEL_GAP + m['content_h_tail']

    col_widths = [max(meta[r][c]['content_w'] for r in range(n_rows)) + 2 * (CELL_PADDING + CELL_BORDER)
                  for c in range(n_cols)]
    row_heights = [max(meta[r][c]['content_h'] for c in range(n_cols)) + 2 * (CELL_PADDING + CELL_BORDER)
                   for r in range(n_rows)]

    title_w, title_h, title_bx, title_by = text_metrics(title_font, sheet['title'])
    footer_w, footer_h, footer_bx, footer_by = text_metrics(body_font, DELTA_E_FOOTER)

    table_width = sum(col_widths) + CELL_SPACING * (n_cols - 1)
    content_width = max(table_width, title_w, footer_w)
    canvas_w = MARGIN * 2 + content_width

    table_top = MARGIN + title_h + TITLE_GAP
    table_height = sum(row_heights) + CELL_SPACING * (n_rows - 1)
    footer_top = table_top + table_height + FOOTER_GAP
    canvas_h = footer_top + footer_h + MARGIN

    xs, x = [], MARGIN
    for c in range(n_cols):
        xs.append(x)
        x += col_widths[c] + CELL_SPACING
    ys, y = [], table_top
    for r in range(n_rows):
        ys.append(y)
        y += row_heights[r] + CELL_SPACING

    cells = [[None] * n_cols for _ in range(n_rows)]
    for r in range(n_rows):
        for c in range(n_cols):
            m = meta[r][c]
            bx, by, bw, bh = xs[c], ys[r], col_widths[c], row_heights[r]
            inner_x, inner_y = bx + CELL_BORDER + CELL_PADDING, by + CELL_BORDER + CELL_PADDING
            entry = {'border_box': (bx, by, bw, bh), 'kind': m['kind']}
            if m['kind'] == 'label':
                entry.update(text_xy=(inner_x, inner_y), text=m['text'], font=m['font'], bearing=m['bearing'])
            else:
                entry.update(label_xy=(inner_x, inner_y), label_text=m['label'], label_font=label_font,
                             label_bearing=m['label_bearing'])
                # Shared across every cell in every row (see label_line_h above): this is the
                # fix for the cross-column content-origin misalignment.
                content_y = inner_y + label_line_h + LABEL_GAP
                if m['kind'] == 'image':
                    entry.update(image_xy=(inner_x, content_y), image_w=m['image_w'], image_h=m['image_h'],
                                 png=m['png'])
                else:
                    entry.update(text_xy=(inner_x, content_y), text=m['text'], font=body_font,
                                 bearing=m['text_bearing'])
            cells[r][c] = entry

    return {
        'canvas_size': (canvas_w, canvas_h),
        'title_xy': (MARGIN, MARGIN), 'title_text': sheet['title'], 'title_font': title_font,
        'title_bearing': (title_bx, title_by),
        'footer_xy': (MARGIN, footer_top), 'footer_text': DELTA_E_FOOTER,
        'footer_bearing': (footer_bx, footer_by),
        'cells': cells,
    }


# --- Drawing -----------------------------------------------------------------------------
def draw_sheet(sheet, layout) -> Image.Image:
    canvas = Image.new('RGB', layout['canvas_size'], BG)
    draw = ImageDraw.Draw(canvas)

    tx, ty = layout['title_xy']
    tbx, tby = layout['title_bearing']
    draw.text((tx - tbx, ty - tby), layout['title_text'], font=layout['title_font'], fill=FG)

    fx, fy = layout['footer_xy']
    fbx, fby = layout['footer_bearing']
    draw.text((fx - fbx, fy - fby), layout['footer_text'], font=load_font(BODY_FONT_SIZE), fill=FG)

    for row in layout['cells']:
        for cell in row:
            bx, by, bw, bh = cell['border_box']
            draw.rectangle([bx, by, bx + bw - 1, by + bh - 1], outline=BORDER_COLOR, width=CELL_BORDER)
            if cell['kind'] == 'label':
                x, y = cell['text_xy']
                bearing_x, bearing_y = cell['bearing']
                draw.text((x - bearing_x, y - bearing_y), cell['text'], font=cell['font'], fill=FG)
                continue
            x, y = cell['label_xy']
            bearing_x, bearing_y = cell['label_bearing']
            draw.text((x - bearing_x, y - bearing_y), cell['label_text'], font=cell['label_font'], fill=FG)
            if cell['kind'] == 'image':
                ix, iy = cell['image_xy']
                with Image.open(io.BytesIO(cell['png'])) as src:
                    src.load()
                    # .convert('RGB') on an opaque source is a byte-for-byte channel copy
                    # (alpha, if any, is simply dropped, never blended); paste() is then a
                    # plain memory copy onto the canvas, so no pixel value is altered.
                    canvas.paste(src.convert('RGB'), (ix, iy))
            else:
                x2, y2 = cell['text_xy']
                bearing_x2, bearing_y2 = cell['bearing']
                draw.text((x2 - bearing_x2, y2 - bearing_y2), cell['text'], font=cell['font'], fill=FG)

    return canvas


def render_sheet(html_text: str) -> bytes:
    sheet = parse_sheet(html_text)
    layout = compute_layout(sheet, default_fonts())
    canvas = draw_sheet(sheet, layout)
    buf = io.BytesIO()
    canvas.save(buf, format='PNG')
    return buf.getvalue()


def main() -> int:
    data = sys.stdin.buffer.read()
    try:
        html_text = data.decode('utf-8')
        png_bytes = render_sheet(html_text)
    except Exception as exc:  # noqa: BLE001 - refuse the whole document, never a partial PNG
        sys.stderr.write(f'export-png: refusing malformed/foreign input: {exc}\n')
        return 1
    sys.stdout.buffer.write(png_bytes)
    sys.stdout.buffer.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
