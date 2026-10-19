# -*- coding: utf-8 -*-
"""Картинки ЛК под реальные размеры вывода (1x, рабочая зона десктопа 1440 px). Исходники — в _sources/.

Запуск из LK v4:  python tools/optimize_images.py

Что и почему такого размера:
- Фон шапки профиля (assets/scenes/lk-hero-<статус>.webp, assets/lk-hero-scene.webp) — 1246×594.
  Кадр Codex (1536×1024) доводится до 2112×1024 (как в v5.1), масштабируется до 1478×717 — размера,
  в котором его показывала шапка, — и обрезается до видимой части: слева 232 px уходили за край,
  снизу 123 px — под край шапки. Ширина 1246 закрывает и десктоп (шапка до 1072 px), и планшет
  1024–1279 px (шапка до ~1231 px). Верхние 45 % кадра плавно уходят в цвет House (--green-house),
  чтобы в высоких шапках не было видно границы фото. Привязка в CSS: left bottom / 1246px 594px.
  13.10: кадр Лиги I (Codex, подиум в один ярус) стоит выше остальных — верх подиума выше на ~26 px исходника
  (~18 px в шапке). SCENE_SHIFT опускает весь кадр на эту величину до остальной обработки: подиум
  встаёт на одну высоту с «без статуса», Лигой II и VIP, освободившийся верх уходит в заливку House.
- Тень карты на подиуме (assets/shadows/card-shadow-<статус>.webp и card-shadow.webp для общего фона, 13.10) —
  мягкий эллипс 320×40 с прозрачностью; в шапке тянется до 88 % ширины карты (~300×34) и при наведении
  увеличивается до ×1.35 — 1x хватает, пятно размытое. Цвет — не карты, а теней самого подиума: в кадре шапки
  берётся поверхность подиума под картой (SHADOW_PROBE) и усредняются её самые тёмные 12 % пикселей без золота —
  затенённая передняя грань, тени листьев. Бетон даёт серую тень, травертин — тёплую, мрамор Super VIP — зелёную.
- Карта участника (assets/cards/lk-card-<статус>.webp) — 360×227 для ≥768 px (карта до 360 px)
  и lk-card-<статус>-720.webp, 720×454, для телефона, где карта во всю ширину.
- Товары (assets/products/*.webp) — длинная сторона 300 px: крупнее всего товар выводится
  в карточке «Избранного» и в рекомендациях, около 250 px.
- Карта в окне адреса (assets/map.webp) — 800 px по ширине: блок карты до ~480×600 px, object-fit cover.
- Карта под шторкой адреса на телефоне (assets/map-sheet.webp, 13.10) — во весь экран телефона до 430×932:
  центральная полоса исходника 440×931 без масштабирования (увеличивать 800-пиксельную карту нельзя — мыло).
- Акции (assets/promo/<код>.webp, 19.10) — локальные копии картинок раздела igrobeauty.ru/personal/promo/
  (исходники 1000×625 JPG в _sources/promo, скачаны 19.10: с сайта они грузились медленно, часть отдавала 404).
  Баннер 720×450: в списке карточка до ~340 px (2x), на странице акции баннер до 720 px.
  Плакаты наборов (<код>-poster.webp) — в полный размер 1305×1819: по ссылке «Открыть плакат целиком»
  должна читаться мелкая таблица состава. tools/build_promo.py берёт локальный файл, если он есть.
"""
import glob
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "_sources")
OUT = os.path.join(ROOT, "assets")
STATUSES = ["none", "l2", "l1", "vip", "svip"]
SCENE_SHIFT = {"l1": 26}  # px исходника 1536×1024: на сколько опустить кадр, чтобы верх подиума совпал с остальными
report = []


def save(im, path, **kw):
    im.save(path, "WEBP", method=6, **kw)
    report.append((os.path.relpath(path, ROOT), im.size, os.path.getsize(path)))


def fit_2112(im):
    """Как tools/fit_scene.py: высота 1024, недостающая ширина справа — зеркальная полоса со склейкой."""
    W, H, BLEND = 2112, 1024, 96
    im = im.convert("RGB")
    w = round(im.width * H / im.height)
    im = im.resize((w, H), Image.LANCZOS)
    if w >= W:
        return im.crop((0, 0, W, H))
    need = W - w
    strip = im.crop((w - need - BLEND, 0, w, H)).transpose(Image.FLIP_LEFT_RIGHT)
    out = Image.new("RGB", (W, H))
    out.paste(im, (0, 0))
    mask = Image.linear_gradient("L").rotate(90).resize((BLEND, H)).transpose(Image.FLIP_LEFT_RIGHT)
    out.paste(Image.composite(im.crop((w - BLEND, 0, w, H)), strip.crop((0, 0, BLEND, H)), mask), (w - BLEND, 0))
    out.paste(strip.crop((BLEND, 0, strip.width, H)), (w, 0))
    return out


def band_dark():
    """Цвет House (--green-house = --band-dark) из токенов DS: в него уходит верх фото."""
    with open(os.path.join(ROOT, "design-system-v6", "tokens", "colors.css"), encoding="utf-8") as f:
        hexv = re.search(r"--green-house:\s*#([0-9a-fA-F]{6})", f.read()).group(1)
    return tuple(int(hexv[i:i + 2], 16) for i in (0, 2, 4))


def scene(im2112, fade=0.45):
    """Видимая часть шапки 1246×594; верхние 45 % плавно уходят в сплошной House.
    Градиент запечён в картинку: в высоких шапках (VIP, Super VIP) нет видимой границы фото,
    а в CSS градиентов нет — их запрещают правила DS."""
    im = im2112.resize((1478, 717), Image.LANCZOS).crop((232, 0, 1478, 594))
    h = round(im.height * fade)
    ramp = Image.linear_gradient("L").resize((1, 256)).resize((im.width, h))  # 0 сверху → 255 снизу
    alpha = Image.new("L", im.size, 255)
    alpha.paste(ramp, (0, 0))
    solid = Image.new("RGB", im.size, band_dark())
    return Image.composite(im, solid, alpha)


def shift_down(im, dy):
    """Опустить кадр на dy px: низ обрезается, верхняя полоса — растянутая первая строка (дальше её всё равно
    заливает переход в House)."""
    im = im.convert("RGB")
    out = Image.new("RGB", im.size)
    out.paste(im.crop((0, 0, im.width, 1)).resize((im.width, dy)), (0, 0))
    out.paste(im.crop((0, 0, im.width, im.height - dy)), (0, dy))
    return out


# Где в кадре шапки 1246×594 лежит поверхность подиума под картой. Кадр стоит у левого нижнего угла шапки
# и опущен на 32 px (lk.css: background-position: left 0 bottom -32px), шапка 533 px, карта — x 32…372,
# тень — 18…52 px над нижним полем 32 px: в координатах кадра это x 60…340, y 487…529. Замер — весь видимый
# подиум под картой: верхняя грань и затенённая передняя (y 487…562; ниже 562 кадр уходит за край шапки).
# Золотые кромки и прожилки отсекаются по насыщенности.
SHADOW_PROBE = (60, 487, 340, 562)


def shadow_tone(scene_im, share=0.12, max_sat=0.5):
    """Цвет теней подиума: средний цвет самых тёмных пикселей (share) на поверхности под картой.
    Насыщенные пиксели (золотая кромка, прожилки) не считаются — нужен цвет тени самого камня."""
    px = [c for c in scene_im.crop(SHADOW_PROBE).convert("RGB").getdata()
          if max(c) and (max(c) - min(c)) / max(c) <= max_sat]
    px.sort(key=lambda c: 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2])
    dark = px[:max(1, int(len(px) * share))]
    return tuple(round(sum(c[i] for c in dark) / len(dark)) for i in range(3))


def card_shadow(color=(8, 20, 14), w=320, h=40, k=4):
    """Мягкая тень карты: эллипс цвета color, края размыты; рисуется в k раз крупнее и уменьшается."""
    a = Image.new("L", (w * k, h * k), 0)
    ImageDraw.Draw(a).ellipse((w * k * 0.08, h * k * 0.28, w * k * 0.92, h * k * 0.72), fill=245)
    a = a.filter(ImageFilter.GaussianBlur(h * k * 0.14)).resize((w, h), Image.LANCZOS)
    im = Image.new("RGBA", (w, h), color + (0,))
    im.putalpha(a)
    return im


def cover(im, w, h):
    im = im.convert("RGB")
    r = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(os.path.join(OUT, "scenes"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "cards"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "products"), exist_ok=True)

    os.makedirs(os.path.join(OUT, "shadows"), exist_ok=True)
    tones = {}
    for k in STATUSES:
        src = Image.open(os.path.join(SRC, "scenes", k + ".png"))
        if k in SCENE_SHIFT:
            src = shift_down(src, SCENE_SHIFT[k])
        sc = scene(fit_2112(src))
        save(sc, os.path.join(OUT, "scenes", "lk-hero-%s.webp" % k), quality=78)
        tones[k] = shadow_tone(sc)
        save(card_shadow(tones[k]), os.path.join(OUT, "shadows", "card-shadow-%s.webp" % k), lossless=True)
    sc = scene(Image.open(os.path.join(SRC, "lk-hero-scene-2112.webp")).convert("RGB"))
    save(sc, os.path.join(OUT, "lk-hero-scene.webp"), quality=78)
    tones["общий фон"] = shadow_tone(sc)
    save(card_shadow(tones["общий фон"]), os.path.join(OUT, "card-shadow.webp"), lossless=True)

    for k in STATUSES:
        src = Image.open(os.path.join(SRC, "cards", "bg-%s.png" % k))
        save(cover(src, 360, 227), os.path.join(OUT, "cards", "lk-card-%s.webp" % k), quality=82)
        save(cover(src, 720, 454), os.path.join(OUT, "cards", "lk-card-%s-720.webp" % k), quality=78)

    for f in sorted(glob.glob(os.path.join(SRC, "products", "*.png"))):
        im = Image.open(f)
        im = im.convert("RGBA") if im.mode in ("RGBA", "LA", "P") else im.convert("RGB")
        im.thumbnail((300, 300), Image.LANCZOS)
        name = os.path.splitext(os.path.basename(f))[0]
        save(im, os.path.join(OUT, "products", name + ".webp"), quality=82)

    m = Image.open(os.path.join(SRC, "map.jpg")).convert("RGB")
    m = m.resize((800, round(m.height * 800 / m.width)), Image.LANCZOS)
    save(m, os.path.join(OUT, "map.webp"), quality=76)
    m0 = Image.open(os.path.join(SRC, "map.jpg")).convert("RGB")
    left = (m0.width - 440) // 2
    save(m0.crop((left, 0, left + 440, m0.height)), os.path.join(OUT, "map-sheet.webp"), quality=74)

    os.makedirs(os.path.join(OUT, "promo"), exist_ok=True)
    for f in sorted(glob.glob(os.path.join(SRC, "promo", "*.jpg"))):
        name = os.path.splitext(os.path.basename(f))[0]
        im = Image.open(f).convert("RGB")
        if name.endswith("-poster"):
            save(im, os.path.join(OUT, "promo", name + ".webp"), quality=80)
        else:
            save(im.resize((720, 450), Image.LANCZOS), os.path.join(OUT, "promo", name + ".webp"), quality=80)

    total = 0
    for path, size, b in report:
        total += b
        print("%-34s %4d×%-4d %4d КБ" % (path, size[0], size[1], round(b / 1024)))
    print("итого %d файлов, %d КБ" % (len(report), round(total / 1024)))
    print("цвет теней подиума: " + ", ".join("%s #%02x%02x%02x" % ((k,) + c) for k, c in tones.items()))


if __name__ == "__main__":
    main()
