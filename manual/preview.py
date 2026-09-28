"""Render a list of SVG strings to a PNG contact sheet for visual checking (dev tool)."""
import sys, pathlib
from weasyprint import HTML
import pypdfium2 as pdfium

def sheet(svgs, out, cols=4, w_mm=45, labels=None):
    cells = "".join(f'<div class="c"><div class="i">{s}</div><div class="l">{(labels or [""]*len(svgs))[i]}</div></div>' for i, s in enumerate(svgs))
    css = f"""@page{{size:{cols*w_mm+10}mm 400mm;margin:5mm}} body{{margin:0;font:7pt Inter}}
    .c{{display:inline-block;width:{w_mm-3}mm;margin:1mm;vertical-align:top;border:.3pt solid #ddd}}
    .i svg{{width:100%;height:auto;display:block}} .l{{text-align:center}}"""
    root = pathlib.Path(__file__).parent
    fonts = (root/'style.css').read_text().split(':root')[0]
    html = f"<html><head><style>{fonts}{css}</style></head><body>{cells}</body></html>"
    pdf = HTML(string=html, base_url=str(root)).write_pdf()
    doc = pdfium.PdfDocument(pdf)
    for i in range(len(doc)):
        img = doc[i].render(scale=2.2).to_pil()
        # crop whitespace
        import PIL.ImageOps
        bbox = PIL.ImageOps.invert(img.convert('RGB')).getbbox()
        if bbox: img = img.crop((0, 0, img.size[0], min(img.size[1], bbox[3] + 20)))
        img.save(out if i == 0 else out.replace('.png', f'-{i}.png'))

def pdf_pages(pdf_path, pages, out_prefix, scale=1.4):
    doc = pdfium.PdfDocument(pdf_path)
    outs = []
    for p in pages:
        img = doc[p-1].render(scale=scale).to_pil()
        fn = f"{out_prefix}-p{p}.png"; img.save(fn); outs.append(fn)
    return outs

if __name__ == "__main__":
    pdf, pages, prefix = sys.argv[1], [int(x) for x in sys.argv[2].split(',')], sys.argv[3]
    print(pdf_pages(pdf, pages, prefix, float(sys.argv[4]) if len(sys.argv) > 4 else 1.4))


def montage(pdf_path, pages, out, cols=3, scale=0.9):
    import PIL.Image
    doc = pdfium.PdfDocument(pdf_path)
    ims = [doc[p - 1].render(scale=scale).to_pil() for p in pages if p - 1 < len(doc)]
    w = max(i.size[0] for i in ims); h = max(i.size[1] for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sheet = PIL.Image.new("RGB", (cols * w + (cols + 1) * 8, rows * h + (rows + 1) * 8), "#888")
    for k, im in enumerate(ims):
        r, c = divmod(k, cols)
        sheet.paste(im, (8 + c * (w + 8), 8 + r * (h + 8)))
    sheet.save(out)
