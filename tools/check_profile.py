# -*- coding: utf-8 -*-
"""Сводка по собранным состояниям профиля: что на карте, в плитках, на шкале, в «лестнице», сколько вопросов.
Запуск из LK v4: python tools/check_profile.py"""
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["profile-p1.html", "index.html", "profile-p3.html", "profile-p4.html", "profile-p5.html"]  # k1–k5 убраны 13.10


def strip(h):
    return re.sub(r"<[^>]+>", "", h).replace("&nbsp;", " ").strip()


for f in FILES:
    h = io.open(os.path.join(ROOT, f), encoding="utf-8").read()
    state = re.search(r'data-lk-state="(\w+)"', h).group(1)
    league = strip(re.search(r'<span class="lk-member-card__league[^"]*">(.*?)</span>', h).group(1))
    since = "В клубе с" in h
    perks = re.findall(r'<li class="(lk-perk[^"]*)">\s*<svg.*?</svg>\s*<span class="lk-perk__value[^"]*">(.*)\n(?:\s*<span class="lk-perk__label">(.*?)</span>)?', h)
    print("=== %s (%s): карта «%s»%s" % (f, state, league, "" if since else " · без «В клубе с…»"))
    retro = re.search(r'<p class="lk-retro[^"]*">(.*?)</p>', h, re.S)
    print("   ретро-бонус в шапке: %s" % (re.sub(r"\s+", " ", strip(re.sub(r'<span class="lk-retro__note">', " / ", retro.group(1)))) if retro else "нет"))
    for cls, v, lab in perks:
        mods = " ".join(c.replace("lk-perk--", "") for c in cls.split() if c.startswith("lk-perk--"))
        print("   плитка%s: %s — %s" % (" [%s]" % mods if mods else "", strip(v), strip(lab or "")[:70]))
    if 'id="level-title"' in h:
        title = strip(re.search(r'id="level-title">(.*?)</h2>', h).group(1))
        lead = strip(re.search(r'<div class="lk-level__goal">\s*(.*?)\s*<p class="lk-level__amount">', h, re.S).group(1))
        amount = strip(re.search(r'<p class="lk-level__amount">(.*?)</p>', h).group(1))
        here = strip(re.search(r'<span class="lk-progress__here"[^>]*>(.*?)<span', h).group(1))
        ends = [strip(x) for x in re.findall(r'<span class="lk-progress__end">(.*?)</span>\s*</span>', h, re.S)]
        vt = re.search(r'aria-valuetext="([^"]*)"', h).group(1).replace("&nbsp;", " ")
        steps = re.findall(r'<li class="lk-ladder__step"( aria-current="step")?>\s*(?:<span class="igro-badge[^"]*">(.*?)</span>)?\s*<div class="lk-ladder__block([^"]*)">.*?<span class="lk-ladder__name">(.*?)</span>.*?<use href="#i-(\w+)"></use></svg>(.*?)</span>', h, re.S)
        print("   блок: «%s» · %s → %s · %s" % (title, lead, amount, here))
        print("   шкала: %s  |  %s" % (" — ".join(ends), vt))
        print("   лестница: " + " | ".join("%s%s %s:%s" % (n, " [" + b + "]" if b else "", ic, strip(g)) for cur, b, m, n, ic, g in steps))
    else:
        print("   блока уровня нет")
    print("   FAQ: %d вопросов · текущее в переключателе: %s" % (h.count("igro-accordion__item"), re.search(r'<option value="([^"]+)" selected>', h).group(1)))
