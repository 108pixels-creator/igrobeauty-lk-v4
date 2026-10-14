# -*- coding: utf-8 -*-
"""Приводит сгенерированный фон шапки к формату assets/lk-hero-scene.webp: 2112×1024, WebP.

Codex отдаёт кадр ~3:2. Он масштабируется по высоте до 1024 px, а недостающая ширина справа
добирается зеркальной полосой стены и пола (как в v5.1), с плавной склейкой. Тогда CSS-привязка
`.lk-hero--scene` (left -232px bottom -123px / 1478px auto) подходит без изменений.

python tools/fit_scene.py <вход.png> <выход.webp>
"""
import sys
from PIL import Image

W, H, BLEND = 2112, 1024, 96


def fit(src, dst):
    im = Image.open(src).convert("RGB")
    w = round(im.width * H / im.height)
    im = im.resize((w, H), Image.LANCZOS)
    if w >= W:
        out = im.crop((0, 0, W, H))
    else:
        need = W - w
        strip = im.crop((w - need - BLEND, 0, w, H)).transpose(Image.FLIP_LEFT_RIGHT)
        out = Image.new("RGB", (W, H))
        out.paste(im, (0, 0))
        # зеркальная полоса начинается с плавного перехода шириной BLEND
        mask = Image.linear_gradient("L").rotate(90).resize((BLEND, H))
        mask = mask.transpose(Image.FLIP_LEFT_RIGHT)
        seam = Image.composite(im.crop((w - BLEND, 0, w, H)), strip.crop((0, 0, BLEND, H)), mask)
        out.paste(seam, (w - BLEND, 0))
        out.paste(strip.crop((BLEND, 0, strip.width, H)), (w, 0))
    out.save(dst, "WEBP", quality=82, method=6)
    print("%s -> %s %dx%d (кадр %dx%d)" % (src, dst, W, H, w, H))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fit(sys.argv[1], sys.argv[2])
