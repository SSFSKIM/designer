"""TDD for export-png.py: HTML->PNG for W41 eye sheets, bounded to this directory.

export-png.py has a hyphenated filename (matching the sibling sheets.ts/render-calval.ts
naming), so it cannot be `import`ed as a module name; it is loaded by path with importlib,
the same technique sheets.ts itself uses to load hyphen/date-named python files.

Every embedded image in these tests is a synthetic inline PNG built in-process with Pillow.
No native/capture PNG is read, matching the assignment: this is a rendering convenience over
an already-authorized standalone HTML string, not a new capture or native-reader path.
"""
import base64
import importlib.util
import io
import subprocess
import sys
import unittest
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / 'export-png.py'
PYTHON = 'python3.12'

_spec = importlib.util.spec_from_file_location('w41_export_png', MODULE_PATH)
export_png = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export_png)


def escape(s: str) -> str:
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;').replace("'", '&#39;'))


def make_png(width: int, height: int, pixel_fn) -> bytes:
    """pixel_fn(x, y) -> (r, g, b). Every pixel gets a distinct, deterministic value so any
    resample/resize/reorder is detectable by exact-sample comparison, not just an average."""
    img = Image.new('RGB', (width, height))
    for y in range(height):
        for x in range(width):
            img.putpixel((x, y), pixel_fn(x, y))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def checker_pixel(x, y):
    return ((x * 53) % 256, (y * 97) % 256, ((x + y) * 61) % 256)


def image_tag(width, height, png_bytes, label):
    b64 = base64.b64encode(png_bytes).decode('ascii')
    return (f'<img alt="{escape(label)}" width="{width}" height="{height}" '
            f'src="data:image/png;base64,{b64}">')


def panel(content, label, missing='UNMEASURED'):
    if content is None:
        return f'<td><h2>{label}</h2><p>{missing}</p></td>'
    width, height, png_bytes = content
    return f'<td><h2>{label}</h2>{image_tag(width, height, png_bytes, label)}</td>'


def build_sheet_html(title='canonical / apple-macos-27.0-1x-light-standard-glass0.5 / photo__rrect-md__rest',
                      native=None, gpu=None, candidate=None, delta_gpu=None, delta_candidate=None,
                      candidate_present=True, table_aria_label='Native and WebGPU comparison',
                      table_tag='table', row_count=2, col_count=3):
    """Faithful reproduction of renderCell()'s exact standalone-HTML shape (sheets.ts), with
    synthetic inline PNGs substituted for real captures. Structural knobs (aria label / tag /
    row / col counts) exist only so malformed-input tests can mutate one axis at a time."""
    candidate_missing = 'UNMEASURED' if candidate_present else 'EMPTY — awaiting G2 document'
    cells_row1 = [panel(native, 'Native'), panel(gpu, 'Shipped WebGPU'),
                  panel(candidate, 'Candidate', candidate_missing)]
    cells_row2 = ['<td>Difference from native</td>', panel(delta_gpu, 'Shipped ΔE × 8'),
                  panel(delta_candidate, 'Candidate ΔE × 8', candidate_missing)]
    row1 = ''.join(cells_row1[:col_count])
    row2 = ''.join(cells_row2[:col_count])
    rows_html = f'<tr>{row1}</tr>\n<tr>{row2}</tr>'
    if row_count == 1:
        rows_html = f'<tr>{row1}</tr>'
    elif row_count > 2:
        rows_html = rows_html + f'\n<tr>{row1}</tr>'
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>{escape(title)}</title>
<style>body{{font:14px system-ui;color:#111;background:white;margin:24px}}table{{border-spacing:8px}}
 td{{vertical-align:top;border:1px solid #aaa;padding:8px}}h2{{font-size:16px}}img{{display:block}}
 code{{overflow-wrap:anywhere}}p{{max-width:100ch}}</style><h1>{escape(title)}</h1>
<p>ΔE × 8: OKLab distance; black = 0, white = 0.125 or greater (clipped). Original pixel dimensions.
The native reader, not this sheet, owns exposure authorization and repeat selection.</p>
<{table_tag} aria-label="{escape(table_aria_label)}">{rows_html}</{table_tag}>
<p>Shipped documents: <code>[{{"kind":"materialProfile","path":"profiles/x.json","sha256":"abc123abc123"}}]</code></p>
<p>Candidate documents: <code>none</code></p>
<p>Capture root: <code>/tmp/example-captures</code>. Missing captures are UNMEASURED, never blank successes.</p></html>'''


class ParseWellFormedTests(unittest.TestCase):
    def test_full_sheet_all_six_cells_present(self):
        png = make_png(3, 2, checker_pixel)
        html = build_sheet_html(
            native=(3, 2, png), gpu=(3, 2, png), candidate=(3, 2, png),
            delta_gpu=(3, 2, png), delta_candidate=(3, 2, png))
        sheet = export_png.parse_sheet(html)
        self.assertIn('photo__rrect-md__rest', sheet['title'])
        self.assertEqual(len(sheet['rows']), 2)
        self.assertEqual(len(sheet['rows'][0]), 3)
        self.assertEqual(len(sheet['rows'][1]), 3)
        labels_row1 = [c['label'] for c in sheet['rows'][0]]
        self.assertEqual(labels_row1, ['Native', 'Shipped WebGPU', 'Candidate'])
        self.assertEqual(sheet['rows'][1][0]['kind'], 'label')
        self.assertEqual(sheet['rows'][1][0]['text'], 'Difference from native')
        self.assertEqual(sheet['rows'][1][1]['label'], 'Shipped ΔE × 8')
        for r in (0, 1):
            for c in (0, 1, 2) if r == 0 else (1, 2):
                cell = sheet['rows'][r][c]
                self.assertEqual(cell['kind'], 'image')
                self.assertEqual((cell['width'], cell['height']), (3, 2))
                self.assertEqual(cell['png'], png)

    def test_missing_cells_carry_exact_text(self):
        html = build_sheet_html(native=None, gpu=None, candidate=None, delta_gpu=None,
                                 delta_candidate=None, candidate_present=False)
        sheet = export_png.parse_sheet(html)
        self.assertEqual(sheet['rows'][0][0]['kind'], 'missing')
        self.assertEqual(sheet['rows'][0][0]['text'], 'UNMEASURED')
        self.assertEqual(sheet['rows'][0][2]['text'], 'EMPTY — awaiting G2 document')
        self.assertEqual(sheet['rows'][1][2]['text'], 'EMPTY — awaiting G2 document')

    def test_mixed_present_and_missing(self):
        png = make_png(4, 4, checker_pixel)
        html = build_sheet_html(native=(4, 4, png), gpu=(4, 4, png), candidate=None,
                                 delta_gpu=(4, 4, png), delta_candidate=None, candidate_present=False)
        sheet = export_png.parse_sheet(html)
        self.assertEqual(sheet['rows'][0][0]['kind'], 'image')
        self.assertEqual(sheet['rows'][0][2]['kind'], 'missing')
        self.assertEqual(sheet['rows'][1][1]['kind'], 'image')
        self.assertEqual(sheet['rows'][1][2]['kind'], 'missing')


class MalformedRefusalTests(unittest.TestCase):
    def assert_refuses(self, html):
        with self.assertRaises(Exception):
            export_png.parse_sheet(html)

    def test_wrong_table_tag_is_foreign(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 delta_gpu=(2, 2, png), delta_candidate=(2, 2, png))
        html = html.replace('<table aria-label', '<div data-fake aria-label').replace('</table>', '</div>')
        self.assert_refuses(html)

    def test_wrong_aria_label_is_foreign(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 delta_gpu=(2, 2, png), delta_candidate=(2, 2, png),
                                 table_aria_label='Some other table')
        self.assert_refuses(html)

    def test_too_few_rows(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 row_count=1)
        self.assert_refuses(html)

    def test_too_many_rows(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 delta_gpu=(2, 2, png), delta_candidate=(2, 2, png), row_count=3)
        self.assert_refuses(html)

    def test_too_few_columns(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 delta_gpu=(2, 2, png), delta_candidate=(2, 2, png), col_count=2)
        self.assert_refuses(html)

    def test_no_table_at_all(self):
        self.assert_refuses('<!doctype html><html lang="en"><h1>hello</h1><p>no table here</p></html>')

    def test_completely_foreign_document(self):
        self.assert_refuses('<!doctype html><html><body><div class="app"><h1>Unrelated</h1></div></body></html>')

    def test_unclosed_html_tag(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 delta_gpu=(2, 2, png), delta_candidate=(2, 2, png))
        html = html[:-len('</html>')]
        self.assert_refuses(html)

    def test_mismatched_closing_tag(self):
        html = '<html lang="en"><h1>title</h1><table aria-label="Native and WebGPU comparison">' \
               '<tr><td>a</td></section></html>'
        self.assert_refuses(html)

    def test_bottom_left_cell_is_not_a_bare_label(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 delta_gpu=(2, 2, png), delta_candidate=(2, 2, png))
        html = html.replace('<td>Difference from native</td>',
                             '<td><h2>Difference from native</h2></td>')
        self.assert_refuses(html)

    def test_top_row_cannot_carry_a_bare_label(self):
        png = make_png(2, 2, checker_pixel)
        html = build_sheet_html(native=(2, 2, png), gpu=(2, 2, png), candidate=(2, 2, png),
                                 delta_gpu=(2, 2, png), delta_candidate=(2, 2, png))
        html = html.replace(panel((2, 2, png), 'Native'), '<td>Native</td>', 1)
        self.assert_refuses(html)

    def test_td_content_is_neither_image_nor_paragraph(self):
        html = build_sheet_html()
        html = html.replace('<p>UNMEASURED</p>', '<div>UNMEASURED</div>', 1)
        self.assert_refuses(html)

    def test_corrupt_base64_refuses(self):
        html = build_sheet_html()
        bad_tag = '<img alt="Native" width="2" height="2" src="data:image/png;base64,***not-base64***">'
        html = html.replace('<td><h2>Native</h2><p>UNMEASURED</p></td>', f'<td><h2>Native</h2>{bad_tag}</td>', 1)
        self.assert_refuses(html)

    def test_bytes_that_decode_but_are_not_a_png_refuses(self):
        html = build_sheet_html()
        junk_b64 = base64.b64encode(b'this is not png data at all, just text').decode('ascii')
        bad_tag = f'<img alt="Native" width="2" height="2" src="data:image/png;base64,{junk_b64}">'
        html = html.replace('<td><h2>Native</h2><p>UNMEASURED</p></td>', f'<td><h2>Native</h2>{bad_tag}</td>', 1)
        self.assert_refuses(html)

    def test_declared_dimensions_lie_about_actual_png_size(self):
        png = make_png(3, 2, checker_pixel)
        b64 = base64.b64encode(png).decode('ascii')
        bad_tag = f'<img alt="Native" width="30" height="20" src="data:image/png;base64,{b64}">'
        html = build_sheet_html()
        html = html.replace('<td><h2>Native</h2><p>UNMEASURED</p></td>', f'<td><h2>Native</h2>{bad_tag}</td>', 1)
        self.assert_refuses(html)

    def test_foreign_image_source_is_not_a_data_uri(self):
        html = build_sheet_html()
        bad_tag = '<img alt="Native" width="2" height="2" src="https://example.com/x.png">'
        html = html.replace('<td><h2>Native</h2><p>UNMEASURED</p></td>', f'<td><h2>Native</h2>{bad_tag}</td>', 1)
        self.assert_refuses(html)

    def test_no_h1_title(self):
        html = build_sheet_html()
        html = html.replace('<h1>canonical / apple-macos-27.0-1x-light-standard-glass0.5 / photo__rrect-md__rest</h1>', '')
        self.assert_refuses(html)


class LayoutAndRenderTests(unittest.TestCase):
    def test_no_resize_exact_pixel_preservation_small_image(self):
        w, h = 3, 2
        png = make_png(w, h, checker_pixel)
        html = build_sheet_html(native=(w, h, png), gpu=(w, h, png), candidate=(w, h, png),
                                 delta_gpu=(w, h, png), delta_candidate=(w, h, png))
        sheet = export_png.parse_sheet(html)
        fonts = export_png.default_fonts()
        layout = export_png.compute_layout(sheet, fonts)
        img = export_png.draw_sheet(sheet, layout)
        self.assertEqual(img.size, layout['canvas_size'])
        source = Image.open(io.BytesIO(png)).convert('RGB')
        cell = layout['cells'][0][0]
        self.assertEqual(cell['image_w'], w)
        self.assertEqual(cell['image_h'], h)
        ix, iy = cell['image_xy']
        for x in range(w):
            for y in range(h):
                self.assertEqual(img.getpixel((ix + x, iy + y)), source.getpixel((x, y)),
                                  f'pixel ({x},{y}) altered or resampled')

    def test_no_resize_larger_checkerboard_every_cell(self):
        w, h = 17, 11
        png = make_png(w, h, checker_pixel)
        html = build_sheet_html(native=(w, h, png), gpu=(w, h, png), candidate=(w, h, png),
                                 delta_gpu=(w, h, png), delta_candidate=(w, h, png))
        png_bytes_out = export_png.render_sheet(html)
        img = Image.open(io.BytesIO(png_bytes_out)).convert('RGB')
        sheet = export_png.parse_sheet(html)
        layout = export_png.compute_layout(sheet, export_png.default_fonts())
        source = Image.open(io.BytesIO(png)).convert('RGB')
        sample_points = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, h // 2), (3, 7), (11, 2)]
        checked_cells = 0
        for r, row in enumerate(layout['cells']):
            for c, cell in enumerate(row):
                if cell['kind'] != 'image':
                    continue
                ix, iy = cell['image_xy']
                self.assertEqual((cell['image_w'], cell['image_h']), (w, h))
                for (x, y) in sample_points:
                    self.assertEqual(img.getpixel((ix + x, iy + y)), source.getpixel((x, y)),
                                      f'row {r} col {c} pixel ({x},{y}) altered or resampled')
                checked_cells += 1
        self.assertEqual(checked_cells, 5)

    def test_label_and_title_areas_are_not_clipped(self):
        w, h = 5, 5
        png = make_png(w, h, checker_pixel)
        long_title = ('canonical / apple-macos-27.0-2x-light-standard-glass0.5-receded / '
                       'photo__rrect-md__rest-inactive-a-very-long-scene-identifier')
        html = build_sheet_html(title=long_title, native=(w, h, png), gpu=(w, h, png),
                                 candidate=(w, h, png), delta_gpu=(w, h, png), delta_candidate=(w, h, png))
        sheet = export_png.parse_sheet(html)
        fonts = export_png.default_fonts()
        layout = export_png.compute_layout(sheet, fonts)
        canvas_w, canvas_h = layout['canvas_size']
        title_w, title_h, _, _ = export_png.text_metrics(fonts['title'], sheet['title'])
        tx, ty = layout['title_xy']
        self.assertLessEqual(tx + title_w, canvas_w, 'title text right edge clipped by canvas')
        self.assertLessEqual(ty + title_h, canvas_h, 'title text bottom edge clipped by canvas')
        for row in layout['cells']:
            for cell in row:
                bx, by, bw, bh = cell['border_box']
                if cell['kind'] == 'label':
                    lx, ly = cell['text_xy']
                    lw, lh, _, _ = export_png.text_metrics(cell['font'], cell['text'])
                else:
                    lx, ly = cell['label_xy']
                    lw, lh, _, _ = export_png.text_metrics(cell['label_font'], cell['label_text'])
                self.assertLessEqual(lx + lw, bx + bw, 'label text right edge clipped by its cell border')
                self.assertLessEqual(ly + lh, by + bh, 'label text bottom edge clipped by its cell border')
                if cell['kind'] == 'missing':
                    mx, my = cell['text_xy']
                    mw, mh, _, _ = export_png.text_metrics(cell['font'], cell['text'])
                    self.assertLessEqual(mx + mw, bx + bw, 'missing text right edge clipped')
                    self.assertLessEqual(my + mh, by + bh, 'missing text bottom edge clipped')

    def test_missing_and_title_text_actually_draws_ink(self):
        html = build_sheet_html(native=None, gpu=None, candidate=None, delta_gpu=None,
                                 delta_candidate=None, candidate_present=False)
        png_bytes_out = export_png.render_sheet(html)
        img = Image.open(io.BytesIO(png_bytes_out)).convert('RGB')
        sheet = export_png.parse_sheet(html)
        layout = export_png.compute_layout(sheet, export_png.default_fonts())

        def has_ink(x0, y0, w, h):
            for y in range(max(0, int(y0)), int(y0) + max(1, int(h))):
                for x in range(max(0, int(x0)), int(x0) + max(1, int(w))):
                    if img.getpixel((x, y)) != (255, 255, 255):
                        return True
            return False

        tx, ty = layout['title_xy']
        title_w, title_h, _, _ = export_png.text_metrics(export_png.default_fonts()['title'], sheet['title'])
        self.assertTrue(has_ink(tx, ty, title_w, title_h), 'title text drew no visible ink')
        cell = layout['cells'][0][0]
        mx, my = cell['text_xy']
        mw, mh, _, _ = export_png.text_metrics(cell['font'], cell['text'])
        self.assertTrue(has_ink(mx, my, mw, mh), 'UNMEASURED text drew no visible ink')

    def test_colors_are_light_background_dark_text(self):
        self.assertEqual(export_png.BG, (255, 255, 255))
        self.assertEqual(export_png.FG, (0x11, 0x11, 0x11))
        html = build_sheet_html(native=None, gpu=None, candidate=None, delta_gpu=None,
                                 delta_candidate=None, candidate_present=False)
        png_bytes_out = export_png.render_sheet(html)
        img = Image.open(io.BytesIO(png_bytes_out)).convert('RGB')
        self.assertEqual(img.getpixel((0, 0)), (255, 255, 255))

    def test_delta_e_legend_footer_present_and_uses_an_established_font(self):
        html = build_sheet_html(native=None, gpu=None, candidate=None, delta_gpu=None,
                                 delta_candidate=None, candidate_present=False)
        sheet = export_png.parse_sheet(html)
        layout = export_png.compute_layout(sheet, export_png.default_fonts())
        self.assertIn('footer_text', layout)
        self.assertIn('ΔE', layout['footer_text'])
        self.assertIn('0.125', layout['footer_text'])
        canvas_w, canvas_h = layout['canvas_size']
        fx, fy = layout['footer_xy']
        fw, fh, _, _ = export_png.text_metrics(export_png.default_fonts()['body'], layout['footer_text'])
        self.assertLessEqual(fx + fw, canvas_w, 'footer legend clipped horizontally')
        self.assertLessEqual(fy + fh, canvas_h, 'footer legend clipped vertically (not included in canvas height)')
        png_bytes_out = export_png.render_sheet(html)
        img = Image.open(io.BytesIO(png_bytes_out)).convert('RGB')
        found_ink = any(img.getpixel((x, int(fy) + fh // 2)) != (255, 255, 255)
                         for x in range(int(fx), int(fx) + int(fw)))
        self.assertTrue(found_ink, 'ΔE legend footer drew no visible ink')


class AlignmentRegressionTests(unittest.TestCase):
    """The fixed table's own column labels differ in descender/ascender shape ("Shipped
    WebGPU" and "Shipped ΔE × 8" both carry a descending 'p'; "Native", "Candidate"
    and "Candidate ΔE × 8" do not). A tight per-cell ink bbox height therefore varies
    by column, and using it to place the content below each label invents a several-pixel
    vertical offset between panels that must otherwise be pixel-comparable."""

    def test_row_image_origins_align_despite_differing_label_descenders(self):
        w, h = 6, 4
        png = make_png(w, h, checker_pixel)
        html = build_sheet_html(native=(w, h, png), gpu=(w, h, png), candidate=(w, h, png),
                                 delta_gpu=(w, h, png), delta_candidate=(w, h, png))
        sheet = export_png.parse_sheet(html)
        layout = export_png.compute_layout(sheet, export_png.default_fonts())
        top_row_ys = [layout['cells'][0][c]['image_xy'][1] for c in (0, 1, 2)]
        self.assertEqual(len(set(top_row_ys)), 1,
                          f'top-row image origins must share one baseline, got {top_row_ys}')
        bottom_row_ys = [layout['cells'][1][c]['image_xy'][1] for c in (1, 2)]
        self.assertEqual(len(set(bottom_row_ys)), 1,
                          f'bottom-row ΔE image origins must share one baseline, got {bottom_row_ys}')

    def test_row_image_origins_still_exact_pixel_after_alignment_fix(self):
        # The fix must move WHERE the image starts, never resample or reorder its bytes.
        w, h = 6, 4
        png = make_png(w, h, checker_pixel)
        html = build_sheet_html(native=(w, h, png), gpu=(w, h, png), candidate=(w, h, png),
                                 delta_gpu=(w, h, png), delta_candidate=(w, h, png))
        png_bytes_out = export_png.render_sheet(html)
        img = Image.open(io.BytesIO(png_bytes_out)).convert('RGB')
        source = Image.open(io.BytesIO(png)).convert('RGB')
        sheet = export_png.parse_sheet(html)
        layout = export_png.compute_layout(sheet, export_png.default_fonts())
        for r, cols in ((0, (0, 1, 2)), (1, (1, 2))):
            for c in cols:
                ix, iy = layout['cells'][r][c]['image_xy']
                for x in range(w):
                    for y in range(h):
                        self.assertEqual(img.getpixel((ix + x, iy + y)), source.getpixel((x, y)),
                                          f'row {r} col {c} pixel ({x},{y}) altered by alignment fix')


class CliContractTests(unittest.TestCase):
    def run_cli(self, html: str):
        return subprocess.run([PYTHON, str(MODULE_PATH)], input=html.encode('utf-8'),
                               capture_output=True, timeout=30)

    def test_well_formed_input_on_stdin_yields_png_on_stdout_exit_zero(self):
        png = make_png(4, 3, checker_pixel)
        html = build_sheet_html(native=(4, 3, png), gpu=(4, 3, png), candidate=(4, 3, png),
                                 delta_gpu=(4, 3, png), delta_candidate=(4, 3, png))
        result = self.run_cli(html)
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
        self.assertTrue(result.stdout.startswith(b'\x89PNG\r\n\x1a\n'))
        img = Image.open(io.BytesIO(result.stdout))
        img.load()

    def test_malformed_input_refuses_with_nonzero_exit_and_no_png_on_stdout(self):
        result = self.run_cli('<!doctype html><html><body>not a sheet</body></html>')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(result.stdout.startswith(b'\x89PNG\r\n\x1a\n'),
                          'a refusal must not silently emit a PNG for a dropped/malformed cell')
        self.assertTrue(len(result.stderr) > 0)


if __name__ == '__main__':
    unittest.main()
