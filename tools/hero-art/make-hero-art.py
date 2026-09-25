#!/usr/bin/env python3
"""Santhi Yoga India: build the layered home-hero painting.

Turns tools/hero-art/source.webp (1376x768 illustration) into the files the home
hero uses in assets/img:

  hero-cosmos-{960,1376,1920,2752}.webp        clean plate (sky, planet, platform, figure)
  hero-cosmos-yogi-{300,600}.webp              the meditating figure, with alpha
  hero-cosmos-isle-left-*.webp / isle-right-*  the two floating islands, with alpha

Steps
  1. Clean   the dark dust trail out of the pastel sky on the left, where the words sit.
  2. Upscale 4x with Real-ESRGAN (x4plus anime 6B), run through onnxruntime so no
             PyTorch is needed, then settle at 2752px wide (2x) for sharp retina edges.
  3. Cut     the figure and the islands out with rembg (isnet-general-use), before
             grading, while the edges still have their full contrast.
  4. Grade   slightly less saturation, highlights leaning to kasavu gold, and a
             luminous morning mist rising from the left edge.
  5. Plate   the islands are removed from the plate and the sky is filled in beneath
             them, so they can drift and parallax without leaving a ghost behind.

It prints each layer's box as a percentage of the picture (the left/top/width in
the .hero-yogi / .hero-isle rules in assets/css/site.css) and the tiny blurred
placeholder used as the stage background. Paste those in if the layers move.

Needs:  pip install pillow numpy scipy onnx onnxruntime "rembg[cpu]"
Run:    python3 tools/hero-art/make-hero-art.py [--out assets/img]
The first run downloads the Real-ESRGAN weights (18 MB, from GitHub) next to this
script and the isnet model (180 MB) into ~/.u2net. Neither is committed.
"""
import argparse, base64, collections, io, json, os, pickle, urllib.request, zipfile
import numpy as np
import onnx
import onnxruntime as ort
from onnx import TensorProto, helper, numpy_helper
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ESRGAN_URL = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth'
Image.MAX_IMAGE_PIXELS = None
LUMA = np.array([.2126, .7152, .0722], np.float32)
# Where each layer sits, in pixels of the 2752x1536 master (a loose box around it for rembg)
LAYERS = {'yogi': (1600, 560, 2440, 1300), 'isle-left': (1080, 600, 1520, 1200), 'isle-right': (2440, 380, 2752, 880)}


def smooth(a, b, t):
    t = np.clip((t - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def normalized_fill(img, keep, sigmas):
    """Fill the pixels where keep == 0 from their surroundings, finest scale first."""
    fill = np.zeros_like(img); wsum = np.zeros(img.shape[:2] + (1,), np.float32)
    for sigma in sigmas:
        num = np.stack([ndi.gaussian_filter(img[..., c] * keep, sigma) for c in range(3)], -1)
        den = ndi.gaussian_filter(keep, sigma)[..., None]
        w = np.clip(den * 4, 0, 1) * (1 - wsum)
        fill += num / np.maximum(den, 1e-5) * w; wsum += w
    return fill / np.maximum(wsum, 1e-5)


def clean(im):
    """1. The dust trail: specks darker than the smooth sky around them."""
    a = np.asarray(im).astype(np.float32)
    H, W, _ = a.shape
    L = a @ LUMA
    dark = (ndi.median_filter(L, size=17) - L) > 5
    yy, xx = np.mgrid[0:H, 0:W]
    zone = (xx < 575) & (yy > 150) & (yy < 600) & ~((xx > 470) & (yy < 265))  # clear of island and planet ring
    mask = ndi.binary_dilation(dark & zone, iterations=2)
    fill = normalized_fill(a, (~mask).astype(np.float32), (4, 12))
    fill += np.random.default_rng(7).normal(0, .6, fill.shape).astype(np.float32)
    m = ndi.gaussian_filter(mask.astype(np.float32), .8)[..., None]
    return Image.fromarray(np.clip(a * (1 - m) + fill * m, 0, 255).astype(np.uint8))


def load_torch_zip(path):
    """Read a PyTorch checkpoint's tensors without PyTorch."""
    z = zipfile.ZipFile(path)
    prefix = z.namelist()[0].split('/')[0]
    kinds = {'FloatStorage': np.float32, 'HalfStorage': np.float16}

    class Storage:
        def __init__(self, key, dtype): self.key, self.dtype = key, dtype

    def rebuild(storage, offset, size, stride, *_):
        raw = np.frombuffer(z.read(f'{prefix}/data/{storage.key}'), dtype=storage.dtype)
        return np.lib.stride_tricks.as_strided(raw[offset:], shape=size, strides=[s * raw.itemsize for s in stride]).copy()

    class Unpickler(pickle.Unpickler):
        def find_class(self, mod, name):
            if name in kinds: return name
            if name == '_rebuild_tensor_v2': return rebuild
            if name == 'OrderedDict': return collections.OrderedDict
            return super().find_class(mod, name)

        def persistent_load(self, pid):
            return Storage(pid[2], kinds.get(pid[1], np.float32))

    d = Unpickler(z.open(f'{prefix}/data.pkl')).load()
    return d.get('params_ema', d.get('params', d))


def esrgan_session():
    """Real-ESRGAN's RRDBNet, rebuilt as an ONNX graph from the published weights."""
    pth = os.path.join(HERE, 'RealESRGAN_x4plus_anime_6B.pth')
    if not os.path.exists(pth):
        print('downloading Real-ESRGAN weights'); urllib.request.urlretrieve(ESRGAN_URL, pth)
    W = load_torch_zip(pth)
    nodes, inits, n = [], [], [0]

    def t():
        n[0] += 1; return f't{n[0]}'

    def const(v):
        name = t(); inits.append(numpy_helper.from_array(np.array(v, np.float32), name)); return name

    def op(kind, ins, **kw):
        o = t(); nodes.append(helper.make_node(kind, ins, [o], **kw)); return o

    def conv(x, p):
        for s in ('weight', 'bias'): inits.append(numpy_helper.from_array(W[f'{p}.{s}'].astype(np.float32), f'{p}.{s}'))
        return op('Conv', [x, f'{p}.weight', f'{p}.bias'], pads=[1, 1, 1, 1])

    lrelu = lambda x: op('LeakyRelu', [x], alpha=0.2)
    def rdb(x, p):
        feats = [x]
        for i in range(1, 5): feats.append(lrelu(conv(op('Concat', feats, axis=1) if len(feats) > 1 else x, f'{p}.conv{i}')))
        return op('Add', [op('Mul', [conv(op('Concat', feats, axis=1), f'{p}.conv5'), const(.2)]), x])

    feat = conv('input', 'conv_first'); body = feat
    for i in range(len({k.split('.')[1] for k in W if k.startswith('body.')})):
        o = body
        for j in (1, 2, 3): o = rdb(o, f'body.{i}.rdb{j}')
        body = op('Add', [op('Mul', [o, const(.2)]), body])
    feat = op('Add', [feat, conv(body, 'conv_body')])
    for p in ('conv_up1', 'conv_up2'): feat = lrelu(conv(op('Resize', [feat, '', const([1, 1, 2, 2])], mode='nearest'), p))
    out = conv(lrelu(conv(feat, 'conv_hr')), 'conv_last')
    nodes.append(helper.make_node('Identity', [out], ['output']))
    graph = helper.make_graph(nodes, 'rrdb', [helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 3, None, None])],
                              [helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 3, None, None])], inits)
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid('', 13)]); model.ir_version = 8
    return ort.InferenceSession(model.SerializeToString(), providers=['CPUExecutionProvider'])


def upscale(im, tile=192, pad=16):
    """2. 4x in overlapping tiles, then down to 2x."""
    sess = esrgan_session()
    a = np.asarray(im).astype(np.float32) / 255
    H, W, _ = a.shape
    out = np.zeros((H * 4, W * 4, 3), np.float32)
    for y in range(0, H, tile):
        for x in range(0, W, tile):
            y0, x0, y1, x1 = max(0, y - pad), max(0, x - pad), min(H, y + tile + pad), min(W, x + tile + pad)
            r = sess.run(None, {'input': a[y0:y1, x0:x1].transpose(2, 0, 1)[None]})[0][0].transpose(1, 2, 0)
            th, tw = min(tile, H - y), min(tile, W - x)
            out[y * 4:(y + th) * 4, x * 4:(x + tw) * 4] = r[(y - y0) * 4:(y - y0 + th) * 4, (x - x0) * 4:(x - x0 + tw) * 4]
        print(f'  upscaled rows to {min(H, y + tile)}/{H}')
    big = Image.fromarray((np.clip(out, 0, 1) * 255 + .5).astype(np.uint8))
    return big.resize((W * 2, H * 2), Image.LANCZOS)


def grade(im):
    """4. Colour and the mist on the left."""
    img = np.asarray(im).astype(np.float32) / 255
    H, W, _ = img.shape
    v, u = [g.astype(np.float32) for g in np.mgrid[0:H, 0:W]]
    u, v = u / W, v / H
    lum = (img @ LUMA)[..., None]
    img = lum + (img - lum) * .9
    img = img * (1 + (np.array([1.035, 1, .955], np.float32) - 1) * smooth(.45, 1, lum))
    top, mid, bot = [np.array(c, np.float32) / 255 for c in ((242, 238, 244), (249, 241, 234), (250, 246, 238))]
    tv = v[..., None]
    mist = np.where(tv < .5, top + (mid - top) * (tv / .5), mid + (bot - mid) * ((tv - .5) / .5))
    a = (.68 * (1 - smooth(.03, .52, u)))[..., None]
    return np.clip(img * (1 - a) + mist * a, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(HERE, '..', '..', 'assets', 'img'))
    args = ap.parse_args()
    from rembg import new_session, remove

    print('1. cleaning the sky'); src = clean(Image.open(os.path.join(HERE, 'source.webp')).convert('RGB'))
    print('2. upscaling'); master = upscale(src)
    print('3. cutting layers')
    seg = new_session('isnet-general-use')
    H, W = master.height, master.width
    alpha = {}
    for name, (x0, y0, x1, y1) in LAYERS.items():
        m = np.asarray(remove(master.crop((x0, y0, x1, y1)), session=seg, only_mask=True)).astype(np.float32) / 255
        full = np.zeros((H, W), np.float32); full[y0:y1, x0:x1] = np.where(m < .03, 0, m)
        alpha[name] = full
    print('4. grading'); img = grade(master)

    print('5. plate')
    hole = np.zeros((H, W), bool)
    for name in ('isle-left', 'isle-right'): hole |= ndi.binary_dilation(alpha[name] > .02, iterations=5)
    fill = normalized_fill(img, (~hole).astype(np.float32), (10, 24, 60))
    rng = np.random.default_rng(3)
    fill += rng.normal(0, .004, fill.shape).astype(np.float32)
    ys, xs = np.nonzero(hole)
    for _ in range(90):  # a few faint stars, so the patched sky is not suspiciously empty
        i = rng.integers(len(ys)); cy, cx = ys[i], xs[i]; r = rng.uniform(.8, 2.2)
        sl = np.s_[max(0, cy - 5):min(H, cy + 6), max(0, cx - 5):min(W, cx + 6)]
        gy, gx = np.mgrid[sl]
        g = np.exp(-((gy - cy) ** 2 + (gx - cx) ** 2) / (2 * r * r))[..., None]
        fill[sl] += (1 - fill[sl]) * g * rng.uniform(.25, .7)
    ha = ndi.gaussian_filter(hole.astype(np.float32), 3)[..., None]
    plate = np.clip(img * (1 - ha) + fill * ha, 0, 1)

    to8 = lambda x: (np.clip(x, 0, 1) * 255 + .5).astype(np.uint8)
    os.makedirs(args.out, exist_ok=True)
    save = lambda im, name, q, **kw: im.save(os.path.join(args.out, name + '.webp'), 'WEBP', quality=q, method=6, **kw)
    plate_im = Image.fromarray(to8(plate))
    for w in (960, 1376, 1920, 2752):
        save(plate_im if w == W else plate_im.resize((w, round(H * w / W)), Image.LANCZOS), f'hero-cosmos-{w}', 80 if w < W else 76)
    layout = {}
    for name, al in alpha.items():
        ys, xs = np.nonzero(al > .01)
        x0, x1, y0, y1 = max(0, xs.min() - 6), min(W, xs.max() + 7), max(0, ys.min() - 6), min(H, ys.max() + 7)
        layer = Image.fromarray(np.dstack([to8(img[y0:y1, x0:x1]), to8(al[y0:y1, x0:x1])]), 'RGBA')
        for f in (1, .5):
            im = layer if f == 1 else layer.resize((round(layer.width * f), round(layer.height * f)), Image.LANCZOS)
            save(im, f'hero-cosmos-{name}-{im.width}', 84, exact=True)
        layout[name] = {'left': f'{x0 / W * 100:.3f}%', 'top': f'{y0 / H * 100:.3f}%', 'width': f'{(x1 - x0) / W * 100:.3f}%', 'px': f'{x1 - x0}x{y1 - y0}'}
    buf = io.BytesIO(); Image.fromarray(to8(img)).resize((32, 18), Image.LANCZOS).save(buf, 'WEBP', quality=60)
    print(json.dumps(layout, indent=1))
    print('placeholder: data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode())


if __name__ == '__main__':
    main()
